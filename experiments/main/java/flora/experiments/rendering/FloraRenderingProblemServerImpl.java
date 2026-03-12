package flora.experiments.rendering;

import static flora.util.LoggerUtil.getLogger;

import io.grpc.stub.StreamObserver;
import java.util.Optional;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Logger;

class FloraRenderingProblemServerImpl
    extends FloraRenderingProblemServiceGrpc.FloraRenderingProblemServiceImplBase {
  private static final Logger logger = getLogger();

  final LinkedBlockingQueue<RenderingConfiguration> nextConfiguration = new LinkedBlockingQueue<>();
  final LinkedBlockingQueue<RenderingScore> lastScore = new LinkedBlockingQueue<>();

  final AtomicReference<Optional<RenderingScore>> currentScore =
      new AtomicReference<>(Optional.empty());

  FloraRenderingProblemServerImpl() {}

  @Override
  public void nextConfiguration(
      Empty request, StreamObserver<RenderingConfiguration> resultObserver) {
    try {
      logger.info("taking next configuration");
      RenderingConfiguration configuration = nextConfiguration.take();
      logger.info(String.format("sending configuration %s", configuration));
      resultObserver.onNext(configuration);
    } catch (Exception e) {
      logger.info("failed to get a new configuration");
    }
    resultObserver.onCompleted();
  }

  @Override
  public void evaluate(RenderingScore request, StreamObserver<Empty> resultObserver) {
    currentScore.set(Optional.empty());
    logger.info(String.format("receiving new score %s", request));
    lastScore.add(request);
    resultObserver.onNext(Empty.getDefaultInstance());
    resultObserver.onCompleted();
  }

  synchronized void fetchLastScore() {
    try {
      logger.info("waiting for next score");
      currentScore.set(Optional.empty());
      currentScore.set(Optional.of(lastScore.take()));
    } catch (Exception e) {
      currentScore.set(Optional.empty());
    }
  }
}
