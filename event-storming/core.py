from enum import Enum


class PostItType(Enum):
    EVENT = "event"
    COMMAND = "command"
    AGGREGATE = "aggregate"
    ACTOR = "actor"
    POLICY = "policy"
    UX_TOUCHPOINT = "ux_touchpoint"


class PostIt:
    def __init__(self, postit_id, content, type="event", position=(0, 0), zone="core"):
        self.id = postit_id  # 唯一标识符（如UUID）
        self.content = content  # 文本内容（如“订单已创建”）
        self.position = position  # 在墙上的坐标（模拟物理位置）
        self.links = []  # 关联的其他贴纸ID（如事件触发的命令）
        if not isinstance(type, PostItType):  # 贴纸类型
            raise ValueError("Invalid PostIt type")
        self.type = type
        self.zone = zone  # 分区

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "position": self.position,
            "links": self.links
        }


class Wall:
    def __init__(self):
        self.postits = {}  # 用字典快速通过ID查找贴纸 {id: PostIt}
        self.timeline = []  # 按时间顺序存储事件ID（模拟时间流）
        self.graph = {}  # 邻接表表示贴纸关系 {id: [linked_ids]}
        self.reverse_graph = {} # 逆邻接表

    def add_postit(self, postit):
        if postit.id not in self.postits:
            self.postits[postit.id] = postit
            if postit.type == "event":
                self.timeline.append(postit.id)  # 事件按时间排序
            return True
        return False

    def link_postits(self, source_id, target_id, link_type="related"):
        if self._has_cycle(source_id, target_id):
            raise ValueError("Circular dependency detected")
        if source_id in self.postits and target_id in self.postits:
            self.postits[source_id].links.append((target_id, link_type))
            self.graph.setdefault(source_id, []).append((target_id, link_type))
            self.reverse_graph.setdefault(target_id, []).append((source_id, link_type))
            return True
        return False

    def remove_postit(self, postit_id):
        if postit_id in self.postits:
            # 清理时间线
            if self.postits[postit_id].type == "event":
                self.timeline = [id for id in self.timeline if id != postit_id]
            # 清理图关系
            del self.graph[postit_id]
            for links in self.graph.values():
                if postit_id in links:
                    links.remove(postit_id)
            # 删除本体
            del self.postits[postit_id]
            return True
        return False

    def get_postits_by_type(self, type_filter):
        return [p for p in self.postits.values() if p.type == type_filter]

    def get_zone_summary(self):
        zones = {}
        for p in self.postits.values():
            zones[p.zone] = zones.get(p.zone, 0) + 1
        return zones

    # ================== 工具方法 ========================================================================================
    def _has_cycle(self, new_source, current, visited=None):
        visited = visited or set()
        if current in visited:
            return True
        visited.add(current)
        for neighbor in self.graph.get(current, []):
            if self._has_cycle(new_source, neighbor, visited.copy()):
                return True
        return False

    def validate(self):
        errors = []
        # 规则1：每个命令必须被至少一个事件触发
        commands = self.get_postits_by_type(PostItType.COMMAND)
        for cmd in commands:
            if not any(cmd.id in self.reverse_graph.get(event_id, [])
                       for event_id in self.timeline):
                errors.append(f"Command {cmd.content} has no triggering event")
        return errors
