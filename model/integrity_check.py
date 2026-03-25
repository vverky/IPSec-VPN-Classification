from scapy.all import *
import math


class PacketProcessor:
    def __init__(self):
        self.fragments = {}  # {group_key: {complete_id, total_length, fragments}}
        self.output_queue = []  # 已完成的分片组
        self._current_id = 0  # 全局唯一ID生成器

    def _get_new_id(self):
        self._current_id += 1
        return self._current_id

    def _is_ipv4(self, pkt):
        return IP in pkt

    def calculate_total_length(self, group):
        """计算包含原始IP头的总长度"""
        fragments = sorted(group["fragments"], key=lambda x: x[IP].frag)

        if not fragments:
            return -1

        # 获取原始IP包头长度
        original_header_length = fragments[0][IP].ihl * 4

        expected_offset = 0
        for pkt in fragments:
            ip = pkt[IP]
            offset = ip.frag * 8

            if offset != expected_offset:
                return -1

            data_length = ip.len - (ip.ihl * 4)
            expected_offset += data_length

        return expected_offset + original_header_length  # 核心修正

    def process_packet(self, pkt):
        if not self._is_ipv4(pkt):
            return

        ip = pkt[IP]
        group_key = ip.id
        more_fragments = ip.flags.MF

        # 创建新分组
        if group_key not in self.fragments:
            self.fragments[group_key] = {
                "complete_id": self._get_new_id(),
                "total_length": -1,  # 使用-1表示未完成
                "fragments": []
            }

        group = self.fragments[group_key]
        group["fragments"].append(pkt)

        # 处理最后一个分片
        if not more_fragments:
            total_length = self.calculate_total_length(group)
            if total_length != -1:
                self.output_queue.append({
                    "group_key": group_key,
                    "complete_id": group["complete_id"],
                    "total_length": total_length
                })
                del self.fragments[group_key]

    def get_current_group_info(self, pkt):
        if not self._is_ipv4(pkt):
            return {"complete_id": -1, "total_length": -1}

        group_key = pkt[IP].id

        # 查找未完成分组
        if group_key in self.fragments:
            return {
                "complete_id": self.fragments[group_key]["complete_id"],
                "total_length": self.fragments[group_key]["total_length"]
            }

        # 查找已完成分组
        for result in self.output_queue:
            if result["group_key"] == group_key:
                return result

        return {"complete_id": -1, "total_length": -1}

    def get_all_results(self):
        """获取全部分组状态"""
        return self.output_queue + [
            {
                "complete_id": g["complete_id"],
                "total_length": g["total_length"]
            } for g in self.fragments.values()
        ]