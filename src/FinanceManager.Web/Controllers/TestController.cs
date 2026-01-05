using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FinanceManager.Web.Data;
using FinanceManager.Web.Models;

namespace FinanceManager.Web.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TestController : ControllerBase
{
    private readonly AppDbContext _context;

    public TestController(AppDbContext context)
    {
        _context = context;
    }

    /// <summary>
    /// 健康检查接口
    /// </summary>
    [HttpGet("health")]
    public async Task<IActionResult> Health()
    {
        var userCount = await _context.Users.CountAsync();
        var logCount = await _context.AIUsageLogs.CountAsync();

        return Ok(new
        {
            status = "healthy",
            database = "connected",
            timestamp = DateTime.UtcNow,
            userCount = userCount,
            aiUsageLogCount = logCount
        });
    }

    /// <summary>
    /// 创建测试用户
    /// </summary>
    [HttpPost("create-test-user")]
    public async Task<IActionResult> CreateTestUser()
    {
        var testUser = new User
        {
            Username = "testuser",
            Email = "test@example.com",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("123456"),
            Nickname = "测试用户",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        try
        {
            _context.Users.Add(testUser);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                message = "测试用户创建成功",
                user = new
                {
                    testUser.Id,
                    testUser.Username,
                    testUser.Email,
                    testUser.Nickname
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    /// <summary>
    /// 获取所有用户
    /// </summary>
    [HttpGet("users")]
    public async Task<IActionResult> GetAllUsers()
    {
        var users = await _context.Users
            .Select(u => new
            {
                u.Id,
                u.Username,
                u.Email,
                u.Nickname,
                u.CreatedAt
            })
            .ToListAsync();

        return Ok(users);
    }
}
