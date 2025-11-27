class RequestStatus:
    """请求状态常量类（用于回调通知）"""
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


class TaskStatus:
    """任务状态常量类（用于数据库记录任务生命周期）"""
    PENDING = "PENDING"       # 未启动/等待中
    RUNNING = "RUNNING"       # 进行中
    COMPLETED = "COMPLETED"   # 完成（单次任务成功）
    FAILED = "FAILED"         # 失败
    CANCELLED = "CANCELLED"   # 已取消
