namespace FinanceManager.Web.Models;

/// <summary>
/// AI使用记录 (记录用户使用了哪些AI功能)
/// </summary>
public class AIUsageLog
{
    /// <summary>
    /// 记录ID
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// 用户ID (外键)
    /// </summary>
    public int UserId { get; set; }

    /// <summary>
    /// 功能类型: "chat", "image", "video"
    /// </summary>
    public string FunctionType { get; set; } = string.Empty;

    /// <summary>
    /// 用户输入的提示词
    /// </summary>
    public string Prompt { get; set; } = string.Empty;

    /// <summary>
    /// Python返回的任务ID
    /// </summary>
    public string? TaskId { get; set; }

    /// <summary>
    /// 生成结果URL (图片/视频地址)
    /// </summary>
    public string? ResultUrl { get; set; }

    /// <summary>
    /// 状态: "pending", "completed", "failed"
    /// </summary>
    public string Status { get; set; } = "pending";

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 关联的用户
    /// </summary>
    public User? User { get; set; }
}
