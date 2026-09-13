# Arquitectura de preparación HA12

## Decisión

El proveedor de liveness se encapsula detrás de un microservicio adaptador. `identity-service` no conoce Didit, sus credenciales, sus DTO ni su URL. Solamente consume la API normalizada `POST /liveness/verifications`.

## Aplicación de arquitectura hexagonal

| Servicio | Núcleo | Puerto | Adaptador de infraestructura |
|---|---|---|---|
| Identity | `StartLivenessOnboarding` | `LivenessVerificationPort` | `HttpLivenessAdapterClient` |
| Liveness adapter | `VerifyLiveness`, `ChangeActiveProvider` | `LivenessProvider`, `ActiveProviderConfiguration` | `DiditProvider`, `InMemoryActiveProviderConfiguration` |

Los módulos de `domain` y `application` no importan FastAPI, HTTPX ni código de Didit. FastAPI está limitado a `api`; HTTP y configuración concreta están en `infrastructure`.

## Contratos internos

`identity-service` envía al adaptador:

```json
{
  "customer_id": "customer-test-001",
  "evidence_ref": "synthetic-selfie-approved",
  "correlation_id": "ha12-manual-001"
}
```

El adaptador responde:

```json
{
  "verification_id": "didit-...",
  "status": "approved",
  "correlation_id": "ha12-manual-001"
}
```

Ni el contrato de Identity ni el contrato normalizado del adaptador contienen `subject_reference`, `selfie_reference` o `decision`, que son detalles del mock Didit.

## Configuración

`LIVENESS_PROVIDER=didit` inicializa el proveedor activo. La configuración vive en el adaptador y se puede consultar o cambiar mediante sus endpoints administrativos. La implementación actual es volátil en memoria para el entorno experimental; en un despliegue persistente debe reemplazarse por configuración gestionada o almacenamiento persistente sin alterar los casos de uso.

## Evolución que se medirá después

Para el experimento real se agregará una implementación `AlternativeProvider` que cumpla `LivenessProvider` y se registrará en el diccionario de proveedores de `liveness-adapter`. No se modifican `identity-service`, la colección Postman ni el contrato normalizado. La parametrización se cambia a `alternative` y se ejecuta la misma solicitud de onboarding.

