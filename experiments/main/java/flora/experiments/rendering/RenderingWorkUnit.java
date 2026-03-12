package flora.experiments.rendering;

import flora.WorkUnit;
import java.util.concurrent.BlockingQueue;

public final class RenderingWorkUnit implements WorkUnit<RenderingKnobs, RenderingConfiguration> {
  private final RenderingKnobs knobs;
  private final RenderingConfiguration configuration;
  private final BlockingQueue<RenderingConfiguration> nextConfiguration;
  private final Runnable barrier;

  RenderingWorkUnit(
      RenderingKnobs knobs,
      RenderingConfiguration configuration,
      BlockingQueue<RenderingConfiguration> nextConfiguration,
      Runnable barrier) {
    this.knobs = knobs;
    this.configuration = configuration;
    this.nextConfiguration = nextConfiguration;
    this.barrier = barrier;
  }

  @Override
  public RenderingKnobs knobs() {
    return knobs;
  }

  @Override
  public RenderingConfiguration configuration() {
    return configuration;
  }

  @Override
  public void run() {
    nextConfiguration.add(configuration);
    barrier.run();
  }
}
