# Arquitectura visual — Preparación HA12

Estos diagramas complementan el protocolo del experimento. La línea continua representa los componentes que existen en la línea base; `AlternativeProvider` aparece punteado porque será construido y medido en la segunda fase.

## 1. Diagrama de componentes

```mermaid
flowchart LR
    P["Postman\nCliente de prueba"] -->|"POST /onboarding/liveness"| I

    subgraph Identity[identity-service :8001]
        I["API FastAPI\n/onboarding/liveness"] --> U["StartLivenessOnboarding\nCaso de uso"]
        U --> IP["LivenessVerificationPort\nPuerto de salida"]
        IP --> HC["HttpLivenessAdapterClient\nAdaptador HTTP"]
    end

    HC -->|"POST /liveness/verifications"| A

    subgraph Adapter[liveness-adapter :8002]
        A["API FastAPI\n/liveness/verifications"] --> V["VerifyLiveness\nCaso de uso"]
        V --> C["ActiveProviderConfiguration\nProveedor activo"]
        V --> LP["LivenessProvider\nPuerto"]
        LP --> DP["DiditProvider\nAdaptador activo"]
        AP["AlternativeProvider\nFase posterior"] -. "implementa" .-> LP
    end

    DP -->|"POST /v1/liveness/checks"| D
    subgraph Didit[didit-mock :8003]
        D["Contrato simulado Didit"]
    end

    Admin["Postman / administrador"] -->|"GET/PUT /admin/liveness-provider"| C
```

**Lectura:** Identity no posee una dependencia hacia Didit ni hacia `AlternativeProvider`; su dependencia termina en `LivenessVerificationPort`. La selección y los DTO específicos permanecen dentro de `liveness-adapter`.

## 2. Diagrama de despliegue

```mermaid
flowchart TB
    Client["Host local\nPostman"]
    subgraph Docker["Docker Compose network: experimentos_default"]
        IS["identity-service\nFastAPI / puerto interno 8000"]
        LA["liveness-adapter\nFastAPI / puerto interno 8000"]
        DM["didit-mock\nFastAPI / puerto interno 8000"]
        IS -->|"HTTP interno"| LA
        LA -->|"HTTP interno"| DM
    end
    Client -->|"localhost:8001"| IS
    Client -. "administración\nlocalhost:8002" .-> LA
    Client -. "inspección mock\nlocalhost:8003" .-> DM
```

| Servicio | Puerto del host | Health check |
|---|---:|---|
| Identity | 8001 | `GET /health` |
| Adaptador liveness | 8002 | `GET /health` |
| Didit mock | 8003 | `GET /health` |

## 3. Diagrama de clases y puertos

```mermaid
classDiagram
    direction LR

    class LivenessRequest {
      +customer_id: str
      +evidence_ref: str
      +correlation_id: str
    }
    class LivenessResult {
      +verification_id: str
      +status: approved|rejected
      +correlation_id: str
    }
    class StartLivenessOnboarding {
      +execute(request) LivenessResult
    }
    class LivenessVerificationPort {
      <<interface>>
      +verify(request) LivenessResult
    }
    class HttpLivenessAdapterClient {
      +verify(request) LivenessResult
    }

    StartLivenessOnboarding --> LivenessVerificationPort
    LivenessVerificationPort <|.. HttpLivenessAdapterClient
    StartLivenessOnboarding --> LivenessRequest
    StartLivenessOnboarding --> LivenessResult

    class VerificationCommand {
      +customer_id: str
      +evidence_ref: str
      +correlation_id: str
    }
    class VerificationResult {
      +verification_id: str
      +status: approved|rejected
      +correlation_id: str
    }
    class VerifyLiveness {
      +execute(command) VerificationResult
    }
    class LivenessProvider {
      <<interface>>
      +verify(command) VerificationResult
    }
    class DiditProvider {
      +verify(command) VerificationResult
    }
    class AlternativeProvider {
      <<future>>
      +verify(command) VerificationResult
    }
    class ActiveProviderConfiguration {
      <<interface>>
      +get_active_provider() str
      +set_active_provider(name)
    }
    class InMemoryActiveProviderConfiguration

    VerifyLiveness --> LivenessProvider
    VerifyLiveness --> ActiveProviderConfiguration
    LivenessProvider <|.. DiditProvider
    LivenessProvider <|.. AlternativeProvider
    ActiveProviderConfiguration <|.. InMemoryActiveProviderConfiguration
    VerifyLiveness --> VerificationCommand
    VerifyLiveness --> VerificationResult
```

**Punto de extensión:** el proveedor nuevo debe implementar únicamente `LivenessProvider`. El caso de uso `VerifyLiveness`, Identity y los contratos normalizados no cambian.

## 4. Secuencia actual: Didit como proveedor activo

```mermaid
sequenceDiagram
    autonumber
    participant P as Postman
    participant I as Identity API
    participant U as StartLivenessOnboarding
    participant H as HTTP Client
    participant A as Liveness Adapter
    participant C as ActiveProviderConfiguration
    participant D as DiditProvider
    participant M as Didit Mock

    P->>I: POST /onboarding/liveness + correlationId
    I->>U: execute(LivenessRequest)
    U->>H: verify(request)
    H->>A: POST /liveness/verifications
    A->>C: get_active_provider()
    C-->>A: didit
    A->>D: verify(VerificationCommand)
    D->>M: POST /v1/liveness/checks
    M-->>D: check_id, decision=PASSED
    D-->>A: VerificationResult(approved)
    A-->>H: respuesta normalizada
    H-->>I: LivenessResult
    I-->>P: verification_id, status, correlation_id
```

## 5. Secuencia futura: incorporación de `alternative`

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Desarrollador
    participant A as Liveness Adapter
    participant P as Postman
    participant I as Identity API
    participant AP as AlternativeProvider
    participant AM as Mock alterno o sandbox

    Dev->>A: Agrega AlternativeProvider que implementa LivenessProvider
    Dev->>A: Registra "alternative" dentro del adaptador
    P->>A: PUT /admin/liveness-provider {alternative}
    A-->>P: 200 {provider: alternative}
    P->>I: Mismo POST /onboarding/liveness
    I->>A: Misma solicitud normalizada
    A->>AP: verify(command)
    AP->>AM: Contrato específico alterno
    AM-->>AP: Respuesta del proveedor
    AP-->>A: VerificationResult normalizado
    A-->>I: Mismo contrato de respuesta
    I-->>P: Mismo contrato y aserciones verdes
```

## 6. Diagrama de alcance del cambio medido

```mermaid
flowchart LR
    subgraph Unchanged["No se modifican"]
        I[identity-service]
        PC["Colección Postman"]
        DC["docker-compose.yml"]
    end
    subgraph Changed["Único alcance permitido del cambio"]
        LA["liveness-adapter\nAlternativeProvider + registro + pruebas"]
    end
    LA -->|"PUT provider=alternative"| I
    PC --> I
```

La evidencia final se obtiene comparando el commit de línea base contra el commit de `AlternativeProvider`. El resultado de `git diff --name-only` debe listar únicamente rutas bajo `liveness-adapter/`.
