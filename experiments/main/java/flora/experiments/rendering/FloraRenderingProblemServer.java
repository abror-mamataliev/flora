package flora.experiments.rendering;

import static flora.util.LoggerUtil.getLogger;

import flora.MeteringMachine;
import flora.contrib.ears.FloraProblem;
import flora.knob.RangeKnob;
import io.grpc.Grpc;
import io.grpc.InsecureServerCredentials;
import io.grpc.Server;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.logging.Logger;
import org.um.feri.ears.algorithms.moo.nsga2.D_NSGAII;
import org.um.feri.ears.problems.StopCriterion;
import org.um.feri.ears.problems.Task;

public class FloraRenderingProblemServer {
  private static final Logger logger = getLogger();

  private static final Integer PORT = Integer.valueOf(8980);
  private static final Path STATE_FILE_PATH = Path.of("/tmp", "state.json");
  private static final RenderingKnobs DEFAULT_KNOBS =
      RenderingKnobs.newBuilder()
          .setResolutionX(RangeKnob.newBuilder().setStart(100).setEnd(1000).setStep(50))
          .setResolutionY(RangeKnob.newBuilder().setStart(100).setEnd(1000).setStep(50))
          .setAntiAliasMin(RangeKnob.newBuilder().setStart(-2).setEnd(2).setStep(1))
          .setAntiAliasMax(RangeKnob.newBuilder().setStart(-2).setEnd(2).setStep(1))
          .setAmbientOcclusionSamples(RangeKnob.newBuilder().setStart(0).setEnd(96).setStep(1))
          .addAllFilter(List.of("BOX", "GAUSSIAN", "BLACKMAN_HARRIS"))
          .build();

  /** Spins up the server. */
  public static void main(String[] args) throws Exception {
    logger.info(String.format("starting new flora server at localhost:%d", PORT));

    FloraRenderingProblemServerImpl serverImpl = new FloraRenderingProblemServerImpl();
    final Server server =
        Grpc.newServerBuilderForPort(PORT, InsecureServerCredentials.create())
            .addService(serverImpl)
            .build();
    server.start();
    final AtomicReference<D_NSGAII> nsga = new AtomicReference<>();
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread("flora-rendering-problem-server-shutdown") {
              @Override
              public void run() {
                try {
                  System.out.println("shutting down flora server since the JVM is shutting down");
                  if (server != null) {
                    server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
                  }
                  nsga.get().saveState(STATE_FILE_PATH.toString());
                } catch (InterruptedException e) {
                  e.printStackTrace(System.err);
                }
                System.out.println("server shutdown...");
              }
            });
    Files.deleteIfExists(STATE_FILE_PATH);
    try {
      while (true) {
        D_NSGAII nsga1 = new D_NSGAII();
        nsga.set(nsga1);
        if (Files.exists(STATE_FILE_PATH)) {
          nsga1.loadState(STATE_FILE_PATH.toString(), false);
        }
        nsga1.execute(
            new Task<>(
                new FloraProblem<RenderingKnobs, RenderingConfiguration, RenderingWorkUnit>(
                    "flora-rendering-problem-server",
                    new RenderingWorkFactory(
                        DEFAULT_KNOBS, serverImpl.nextConfiguration, serverImpl::fetchLastScore),
                    new MeteringMachine(
                        Map.of(
                            "energy",
                            new RenderingScoreMachine.RenderingScoreMeter(
                                () -> serverImpl.currentScore.get().get().getEnergy()),
                            "runtime",
                            new RenderingScoreMachine.RenderingScoreMeter(
                                () -> serverImpl.currentScore.get().get().getRuntime())))),
                StopCriterion.EVALUATIONS,
                100000,
                0,
                0));
        nsga1.saveState(STATE_FILE_PATH.toString());
      }
    } catch (Exception e) {
      logger.warning(String.format("something failed: %s", e));
      e.printStackTrace();
    }
    logger.info(String.format("terminating flora server at localhost:%d", PORT));
  }
}
