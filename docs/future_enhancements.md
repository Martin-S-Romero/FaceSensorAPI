# Future Enhancements

## Async job queue (videos)
- Use Celery + Redis as a broker.
- Expose `/tasks/{task_id}` to query status and download the processed video.
- Make `FaceCensorService` methods callable from Celery tasks with pure path arguments.

## Logging
- Centralize logging config under `app/src/utils/logging_config.py`.
- Use `logging.getLogger(__name__)` in services and routers.
- Add request/response logging middleware for FastAPI.

## Dependency injection
- Replace simple singletons in `dependencies.py` with a DI container (e.g. `punq` or `wired`).
- Allow swapping implementations of `StorageService` (e.g. local disk vs S3) and `FaceCensorService` for testing.

## Performance & OpenCV/MediaPipe optimizations
- Reuse `FaceCensor` instance across requests instead of instantiating per call when safe.
- Benchmark different blur/pixelation strategies for CPU usage.
- Optionally add GPU-accelerated builds of OpenCV for heavy workloads.

## CI/CD
- Add a GitHub Actions workflow to run unit tests and basic linting on push.
- Build and push the Docker image to a registry on tagged releases.
- Optionally deploy to a container platform (Fly.io, Render, etc.).
