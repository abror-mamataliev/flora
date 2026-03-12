package flora.experiments.rendering;

import flora.WorkFactory;
import java.util.Arrays;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ThreadLocalRandom;

public final class RenderingWorkFactory
    implements WorkFactory<RenderingKnobs, RenderingConfiguration, RenderingWorkUnit> {
  private final RenderingKnobs knobs;
  private final BlockingQueue<RenderingConfiguration> nextConfiguration;
  private final int[] configurationSize;
  private final Runnable barrier;

  public RenderingWorkFactory(
      RenderingKnobs knobs,
      BlockingQueue<RenderingConfiguration> nextConfiguration,
      Runnable barrier) {
    this.knobs = knobs;
    this.nextConfiguration = nextConfiguration;
    this.configurationSize =
        new int[] {
          KnobUtils.getConfigurationCount(knobs.getResolutionX()),
          // Sticking with square images
          // KnobUtils.getConfigurationCount(knobs.getResolutionY()),
          KnobUtils.getConfigurationCount(knobs.getAaMin()),
          KnobUtils.getConfigurationCount(knobs.getAaMax()),
          KnobUtils.getConfigurationCount(knobs.getAoSamples()),
          knobs.getFilterCount()
        };
    this.barrier = barrier;
  }

  @Override
  public RenderingKnobs knobs() {
    return this.knobs;
  }

  /** The number of knobs. */
  @Override
  public int knobCount() {
    return 5;
  }

  /** The number of configurations each knob has. */
  @Override
  public int[] configurationSize() {
    return Arrays.copyOf(configurationSize, configurationSize.length);
  }

  @Override
  public int[] decode(RenderingConfiguration configuration) {
    return new int[0];
  }

  /** Creates a new work unit from the given configuration. */
  @Override
  public RenderingWorkUnit newWorkUnit(int[] configuration) {
    return new RenderingWorkUnit(
        knobs,
        RenderingConfiguration.newBuilder()
            .setResolutionX(KnobUtils.getRangeValue(configuration[0], knobs.getResolutionX()))
            // Sticking with square images for now
            .setResolutionY(KnobUtils.getRangeValue(configuration[0], knobs.getResolutionY()))
            .setAaMin(KnobUtils.getRangeValue(configuration[1], knobs.getAaMin()))
            .setAaMax(KnobUtils.getRangeValue(configuration[2], knobs.getAaMax()))
            .setAoSamples(KnobUtils.getRangeValue(configuration[3], knobs.getAoSamples()))
            .setFilter(knobs.getFilterList().get(configuration[4]))
            .build(),
        nextConfiguration,
        barrier);
  }

  @Override
  public boolean isValid(int[] configuration) {
    return true;
  }

  @Override
  public int[] fixConfiguration(int[] configuration) {
    // check that anti-aliasing (knobs 3 and 4) are properly bounded
    while (KnobUtils.getRangeValue(configuration[1], knobs.getAaMin())
        > KnobUtils.getRangeValue(configuration[2], knobs.getAaMax())) {
      configuration[2]++;
    }
    return configuration;
  }

  @Override
  public int[] randomConfiguration() {
    ThreadLocalRandom random = ThreadLocalRandom.current();
    int resolution = random.nextInt(configurationSize[0]);
    int aaMin = random.nextInt(configurationSize[1]);
    int aaMax = random.nextInt(configurationSize[2]);
    while (KnobUtils.getRangeValue(aaMin, knobs.getAaMin())
        > KnobUtils.getRangeValue(aaMax, knobs.getAaMax())) {
      aaMin = random.nextInt(configurationSize[1]);
      aaMax = random.nextInt(configurationSize[2]);
    }
    return new int[] {
      resolution,
      aaMin,
      aaMax,
      random.nextInt(configurationSize[3]),
      random.nextInt(configurationSize[4])
    };
  }
}
