using System.Text.Json.Serialization;

namespace Backend.Models;

public class ChatResponse
{
  [JsonPropertyName("response")]
  public string Response { get; set; } = string.Empty;

  [JsonPropertyName("history")]
  public ChatHistoryModel? History { get; set; }
}
