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
      resultObserver.onNext(nextConfiguration.take());
    } catch (Exception e) {
      logger.info("failed to get a new configuration");
    }
    resultObserver.onCompleted();
  }

  @Override
  public void evaluate(RenderingScore request, StreamObserver<Empty> resultObserver) {
    currentScore.set(Optional.empty());
    lastScore.add(request);
    resultObserver.onNext(Empty.getDefaultInstance());
    resultObserver.onCompleted();
  }

  synchronized void fetchLastScore() {
    try {
      // if (currentScore.get().isEmpty()) {
      currentScore.set(Optional.empty());
      currentScore.set(Optional.of(lastScore.take()));
      // }
      // return currentScore.get().get();
    } catch (Exception e) {
      // return RenderingScore.getDefaultInstance();
    }
  }
}
