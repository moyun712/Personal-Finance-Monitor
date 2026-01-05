namespace FinanceManager.Web.Models;

/// <summary>
/// 用户实体
/// </summary>
public class User
{
    /// <summary>
    /// 用户ID (主键)
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// 用户名 (唯一)
    /// </summary>
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// 密码哈希值 (不存储明文密码!)
    /// </summary>
    public string PasswordHash { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 昵称
    /// </summary>
    public string? Nickname { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
