using Microsoft.AspNetCore.Mvc;

namespace Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
  private readonly ILogger<HealthController> _logger;

  public HealthController(ILogger<HealthController> logger)
  {
    _logger = logger;
  }

  [HttpGet]
  public IActionResult GetHealth()
  {
    return Ok(new
    {
      status = "healthy",
      timestamp = DateTime.UtcNow,
      service = "Backend API"
    });
  }
}
