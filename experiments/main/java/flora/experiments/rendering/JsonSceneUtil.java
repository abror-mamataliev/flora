package flora.experiments.rendering;

import flora.contrib.ears.FloraProblem;
import flora.util.JsonUtil;
import java.io.PrintWriter;
import java.nio.file.Path;
import org.json.JSONObject;

public final class JsonSceneUtil {
  public static JSONObject toJson(RenderingConfiguration configuration) {
    JSONObject jsonObject = new JSONObject();
    jsonObject.put("width", configuration.getResolutionX());
    jsonObject.put("height", configuration.getResolutionY());
    jsonObject.put("aaMin", configuration.getAaMin());
    jsonObject.put("aaMax", configuration.getAaMax());
    jsonObject.put("aoSamples", configuration.getAoSamples());
    jsonObject.put("filter", configuration.getFilter());
    return jsonObject;
  }

  public static void writeResults(
      FloraProblem<RenderingKnobs, RenderingConfiguration, RenderingWorkUnit> problem, Path path)
      throws Exception {
    JSONObject data = JsonUtil.toJson(problem.getCollector(), JsonSceneUtil::toJson);
    PrintWriter writer = new PrintWriter(path.toFile());
    writer.println(data);
  }

  private JsonSceneUtil() {}
}
