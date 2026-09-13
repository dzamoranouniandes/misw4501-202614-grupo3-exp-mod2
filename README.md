# Preparación del experimento HA12: sustitución de liveness

Este directorio contiene una línea base ejecutable para el experimento de facilidad de modificación. Es un multirepo: cada directorio de servicio tiene su propio `Dockerfile`, dependencias y pruebas.

## Alcance

Se implementa el corte vertical mínimo del onboarding biométrico:

```text
Postman -> identity-service -> liveness-adapter -> didit-mock
```

No se incluyen API Gateway ni BFF móvil porque no son necesarios para validar el desacoplamiento del proveedor de liveness. Todos los servicios usan FastAPI y separación hexagonal: dominio y casos de uso no dependen de HTTP ni de un proveedor específico.

`liveness-adapter` contiene el puerto `LivenessProvider`, el caso de uso de verificación, una implementación Didit y la configuración de proveedor activo. La interfaz pública normaliza la respuesta y no filtra el contrato de Didit.

## Levantar el entorno

Requiere Docker Desktop con Compose v2.

```powershell
docker compose up --build
```

Servicios publicados:

| Servicio | URL |
|---|---|
| Identity / onboarding | http://localhost:8001/docs |
| Adaptador liveness | http://localhost:8002/docs |
| Mock Didit | http://localhost:8003/docs |

## Prueba manual con Postman

Importe `postman/HA12-liveness.postman_collection.json` y ejecute en este orden:

1. `Consultar proveedor activo`.
2. `Onboarding aprobado`.
3. `Onboarding rechazado`.
4. `Ver logs correlacionados` con `docker compose logs liveness-adapter didit-mock`.

El request de onboarding entra siempre por Identity:

```http
POST http://localhost:8001/onboarding/liveness
Content-Type: application/json
X-Correlation-Id: ha12-manual-001

{
  "customer_id": "customer-test-001",
  "evidence_ref": "synthetic-selfie-approved"
}
```

La respuesta se normaliza a `verification_id` y `status`; el proveedor usado se evidencia con el `correlation_id` en logs y no se expone al consumidor.

## Configuración del proveedor

La configuración pertenece al adaptador y se consulta mediante:

```http
GET http://localhost:8002/admin/liveness-provider
```

En esta preparación solo está registrado `didit`. El endpoint `PUT /admin/liveness-provider` permite seleccionar un proveedor ya registrado. En la ejecución posterior del experimento se añadirá el segundo adaptador **solo dentro de `liveness-adapter`**, se registrará y se cambiará esta parametrización sin modificar Identity ni la colección Postman.

## Pruebas

Cada repositorio se prueba de forma independiente:

```powershell
cd identity-service; python -m pytest
cd ../liveness-adapter; python -m pytest
cd ../didit-mock; python -m pytest
```

Los tests no necesitan Docker ni conectarse a servicios externos.

## Evidencia de línea base

Antes de implementar el proveedor alterno, conserve:

- salida de `docker compose ps`;
- colección Postman ejecutada y respuestas;
- logs con el mismo `X-Correlation-Id` en Identity, adaptador y Didit mock;
- commit de esta línea base.

El diff que se mida en la siguiente fase debe compararse contra dicho commit, no contra una versión anterior que no tenía el adaptador.

