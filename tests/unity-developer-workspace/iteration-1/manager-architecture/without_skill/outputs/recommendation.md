# Arquitectura objetivo y migración incremental

La opción más segura no es reemplazar el `GameManager` de una sola vez, sino convertirlo temporalmente en una fachada de compatibilidad y extraer responsabilidades por cortes verticales. Cada entrega debe dejar el juego publicable, permitir volver a la implementación anterior y reducir una dependencia observable.

## Arquitectura objetivo

Usaría un único punto de composición en una escena de arranque. Ese `AppBootstrap` crea y conecta las dependencias de larga vida y conserva solamente un objeto raíz con `DontDestroyOnLoad`. El resto se divide según su ciclo de vida real:

| Ciclo de vida | Responsabilidades | Forma recomendada |
|---|---|---|
| Aplicación | audio, persistencia, coordinación de escenas, adaptador de entrada | servicios pequeños, creados por el punto de composición |
| Sesión/partida | progreso actual, inventario, estadísticas y estado recuperable | objetos C# en memoria más DTO de guardado |
| Escena | navegación de UI, presentación, controladores de combate y bindings locales | contexto explícito de escena que se crea y dispone al cargar/descargar |
| Temporal | comandos, solicitudes, resultados y cálculos | objetos efímeros sin estado global |

La separación principal sería:

```text
AppBootstrap / CompositionRoot
├── AudioService
├── SaveRepository
├── SceneTransitionCoordinator
├── InputGateway
└── GameSession
    └── estado de ejecución y casos de uso

Cada escena aditiva
└── SceneContext
    ├── UiNavigator / presenters
    ├── CombatCoordinator
    └── suscripciones y tareas propiedad de esa escena
```

Los sistemas de dominio y de aplicación deberían ser C# ordinario siempre que no necesiten el ciclo de vida de Unity. Los `MonoBehaviour` quedan como adaptadores: reciben callbacks de Unity, traducen datos y llaman a esos sistemas. Las referencias de escena se conectan mediante campos serializados o mediante el `SceneContext`, no con `GameObject.Find`.

No introduciría por defecto un contenedor de inyección. La inyección manual desde uno o unos pocos puntos de composición es suficiente mientras el grafo sea comprensible. Un contenedor se justificaría después si aparecen muchos scopes, fábricas repetidas, decoradores o una composición manual difícil de mantener. Tampoco usaría ECS/DOTS para resolver acoplamiento: solo tendría sentido en subsistemas con grandes cantidades de entidades y un cuello de botella demostrado mediante profiling.

## Contratos y límites

No hace falta crear una interfaz por clase. Conviene definirlas solamente en límites sustituibles o con efectos externos, por ejemplo:

```csharp
public interface ISaveRepository
{
    Task SaveAsync(SaveData data, CancellationToken cancellationToken);
    Task<SaveData?> LoadAsync(CancellationToken cancellationToken);
}

public interface ISceneTransitionCoordinator
{
    Task TransitionAsync(SceneRequest request, CancellationToken cancellationToken);
}
```

`GameSession` debería ser el propietario inequívoco del estado mutable de la partida. Los dos `ScriptableObject` compartidos pasan a representar únicamente configuración autorada. Al comenzar o cargar una partida, sus valores se copian a objetos de sesión; el guardado serializa DTO, no referencias a assets ni componentes de escena. Así se evita que una ejecución modifique accidentalmente datos compartidos o que el estado sobreviva de forma inesperada durante el desarrollo.

El `GameManager` existente conserva inicialmente su API pública, pero cada método empieza a delegar:

```csharp
public sealed class GameManager : MonoBehaviour
{
    private GameApplication _application = null!;

    public void SaveGame() => _application.RequestSave();
    public void GoToScene(string scene) => _application.RequestTransition(scene);
}
```

Esto permite migrar los consumidores gradualmente. El contrato nuevo no debe exponer el propio `GameManager`; las nuevas características reciben solo la dependencia que utilizan.

## Ciclo de vida de escenas y listeners

El problema de listeners obsoletos necesita una corrección temprana, antes de una reorganización amplia:

- Cada suscripción tiene un propietario y una operación simétrica de liberación. En componentes Unity, una suscripción realizada en `OnEnable` se elimina en `OnDisable`; para objetos C#, se devuelve o conserva un `IDisposable` que pertenece al `SceneContext`.
- No se usan lambdas anónimas que después no puedan desuscribirse. Se conserva el delegado o se utiliza un objeto de suscripción descartable.
- Los eventos globales estáticos se reducen o encapsulan. Un bus global recrearía el mismo acoplamiento oculto que hoy tiene el `GameManager`.
- Las tareas asíncronas iniciadas por una escena reciben cancelación asociada a su scope. Al descargarla se cancelan tareas, se eliminan listeners y solo después se destruyen sus objetos.
- `SceneTransitionCoordinator` es la única autoridad para transiciones. Serializa o rechaza solicitudes concurrentes, bloquea temporalmente la entrada pertinente, dispone el contexto saliente, ejecuta carga/descarga y conecta el contexto entrante.
- La UI pertenece a la escena o flujo que la muestra. El servicio global puede exponer intención de navegación, pero no retener referencias a vistas destruidas.

Una transición debe tener estados explícitos como `Idle`, `Leaving`, `Loading`, `Binding` y `Entering`; eso hace comprobables los reingresos y errores. También debe existir una política definida para una segunda solicitud: ignorarla, ponerla en cola o cancelar la primera, en vez de permitir carreras implícitas.

## Assembly definitions y organización para doce desarrolladores

Introduciría `asmdef` por límites estables, no por carpeta arbitraria. Una estructura posible es:

```text
Game.Contracts
Game.Application
Game.Platform.Unity
Game.Features.Combat
Game.Features.UI
Game.Features.Save
Game.Tests.EditMode
Game.Tests.PlayMode
```

Las referencias deben formar un grafo acíclico: las características pueden depender de contratos y aplicación, mientras que la capa Unity implementa adaptadores. Los ensamblados de pruebas referencian explícitamente lo que prueban. Si dividir todo al inicio produce demasiados errores de compilación, se empieza con `Game.Contracts`, un ensamblado para el código nuevo y los dos de pruebas; los límites restantes se introducen al extraer cada característica.

Para minimizar conflictos entre equipos, cada equipo posee un corte vertical (contratos públicos, implementación, adaptador Unity y pruebas) y los cambios a contratos compartidos se revisan como tales. El `GameManager` deja de ser el archivo central que todos editan.

## Plan de migración

### 0. Congelar comportamiento, no desarrollo

Antes de extraer, elaborar un mapa de quién llama a cada área del `GameManager`, qué eventos publica y qué objetos persisten entre escenas. Añadir pruebas de caracterización para los flujos de mayor riesgo: cargar partida, iniciar combate, abrir/cerrar UI y repetir transiciones aditivas. Registrar identificadores de transición y de suscripción en logs de desarrollo facilitará detectar duplicados.

La salida de esta fase es una lista de comportamientos que deben mantenerse y una métrica inicial: cuántas referencias directas, búsquedas globales y listeners sobreviven a una descarga.

### 1. Corregir propiedad de estado y listeners

Crear `GameSession` y `SaveData`; copiar a la sesión la configuración inicial de los `ScriptableObject` sin mutar los assets. Incorporar una comprobación de desarrollo que avise si esos assets cambian durante Play Mode.

En paralelo, hacer simétricas las suscripciones de UI y añadir un scope descartable por escena. Este cambio puede hacerse manteniendo el `GameManager` como publicador, por lo que reduce el defecto actual sin esperar a la arquitectura final.

### 2. Crear el punto de composición y la fachada

Añadir la escena/prefab de bootstrap, crear una sola raíz persistente y construir allí las dependencias. Convertir el `GameManager` en adaptador que delega, sin cambiar todavía a todos sus consumidores. Incluir protección y diagnóstico ante una segunda raíz persistente, especialmente al abrir escenas de contenido directamente desde el editor.

Añadir los primeros `asmdef` y una regla de dependencia sencilla: el código nuevo no puede llamar a `GameObject.Find` para obtener servicios ni agregar nuevas responsabilidades al `GameManager`.

### 3. Extraer en cortes pequeños

Un orden razonable es:

1. **Audio:** suele tener un contrato pequeño y permite validar la estrategia de delegación.
2. **Entrada:** separar lectura de dispositivos de la intención del juego; los mapas/contextos activos pertenecen al flujo correspondiente.
3. **Guardado:** encapsular IO y mapeo de `GameSession` a `SaveData`; proteger versiones y fallos parciales.
4. **Transiciones y navegación:** centralizar la secuencia y trasladar la UI a scopes de escena.
5. **Combate:** extraer casos de uso y reglas a C# ordinario; mantener animación, física y presentación en adaptadores Unity.

Cada extracción sigue el mismo ciclo: caracterizar comportamiento, definir el contrato mínimo, implementar detrás de la fachada, migrar un consumidor, observar, migrar los restantes y eliminar la ruta anterior. No se mezclan varias extracciones de alto riesgo en el mismo lanzamiento.

### 4. Retirar dependencias ocultas

Reemplazar cada `GameObject.Find` restante por referencia serializada, registro explícito en `SceneContext` o dependencia suministrada por el punto de composición. Una búsqueda local y controlada durante el bootstrap puede ser aceptable como puente, pero no debe convertirse en el mecanismo normal de resolución.

Cuando ningún consumidor dependa de la API antigua, eliminar la fachada `GameManager` y su objeto persistente, conservando solo el bootstrap y los servicios que realmente tienen vida de aplicación.

## Estrategia de pruebas y puertas de entrega

La mayor ganancia inmediata es crear seams de C# que permitan pruebas rápidas:

- **Pruebas C# / EditMode:** reinicio y restauración de `GameSession`, mapeo y versionado de `SaveData`, orden de una transición, política de solicitudes concurrentes, cancelación, reglas de combate y liberación de suscripciones usando dobles simples.
- **PlayMode:** existe una sola raíz después de múltiples cargas; cargar y descargar repetidamente una escena no duplica callbacks; una vista descargada no recibe eventos; una transición fallida recupera entrada/estado; los assets de configuración permanecen sin cambios.
- **Pruebas de humo manuales:** continuar partida, cambio de perfiles/dispositivos, pausa, audio entre escenas y salida durante una transición.

Una extracción está lista para producción cuando:

1. la ruta nueva pasa sus pruebas de caracterización y las específicas del contrato;
2. no añade búsquedas globales ni referencias desde servicios de aplicación a objetos de escena;
3. carga/descarga repetida no aumenta el número de suscriptores ni raíces persistentes;
4. puede revertirse haciendo que la fachada vuelva a delegar a la implementación anterior;
5. sus errores y transiciones dejan señales útiles en logs o telemetría.

Para operaciones con efectos, como guardar o cargar escenas, no ejecutaría en paralelo las rutas vieja y nueva. Se puede comparar en sombra solo lógica pura o resultados serializados sin efectos. Un flag de desarrollo o de lanzamiento controlado puede seleccionar la delegación, pero debe retirarse cuando la migración se estabilice.

## Riesgos a vigilar

- Sustituir un objeto dios por muchos “managers” globales no mejora la arquitectura; cada servicio necesita responsabilidad, dueño y ciclo de vida definidos.
- Un bus de eventos universal o un Service Locator ocultaría de nuevo las dependencias. Los eventos deben tener alcance limitado y propietarios claros.
- Demasiadas interfaces y `asmdef` desde el primer día pueden frenar al equipo. Se agregan al extraer límites reales.
- La persistencia y las transiciones son las áreas con mayor costo de fallo; requieren rollback y pruebas antes de retirar la ruta anterior.
- Pooling, Jobs, ECS/DOTS u otras optimizaciones no forman parte de esta refactorización salvo que mediciones en dispositivos objetivo indiquen un problema concreto.

El primer incremento recomendable es pequeño pero valioso: conservar el `GameManager`, introducir `GameSession`, dejar inmutables los `ScriptableObject`, hacer descartables las suscripciones de una escena problemática y añadir una prueba PlayMode que repita su carga/descarga. Ese incremento valida el modelo de ownership y ataca el defecto observable antes de comenzar las extracciones de servicios.
