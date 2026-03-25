import os
import pandas as pd
from scapy.all import *
import socket
from integrity_check import PacketProcessor

INPUT_DIR = "data"  # 数据集目录
OUTPUT_DIR = "features"
CATEGORIES = ["web", "im", "ftp"]

def process_category(category):
    output_subdir = os.path.join(OUTPUT_DIR, category)
    os.makedirs(output_subdir, exist_ok=True)

    for file_idx in range(1, 201):
        encrypted_path = os.path.join(INPUT_DIR, category, "encrypted", f"{file_idx}.pcapng")
        decrypted_path = os.path.join(INPUT_DIR, category, "decrypted", f"{file_idx}.pcapng")
        output_path = os.path.join(output_subdir, f"{file_idx}.csv")

        try:
            encrypted_pkts = rdpcap(encrypted_path)
            decrypted_pkts = rdpcap(decrypted_path)
        except FileNotFoundError:
            print(f"文件未找到: {encrypted_path} 或 {decrypted_path}")
            continue

        data = []
        # 初始化分片重组模块
        processor = PacketProcessor()
        for pkt_enc, pkt_dec in zip(encrypted_pkts, decrypted_pkts):
            try:
                # === 加密包特征提取 ===
                if not (IP in pkt_enc and ESP in pkt_enc):
                    print(f"加密包缺少必要层，跳过：{pkt_enc.summary()}")
                    continue

                # 数据链路层（以太网头）
                enc_eth = pkt_enc.getlayer(Ether)
                data_len = len(enc_eth) if enc_eth else 0

                # IP层和ESP层解析
                enc_ip = pkt_enc[IP]
                enc_esp = pkt_enc[ESP]
                enc_time = pkt_enc.time  # 时间戳

                ip_header_len = enc_ip.ihl * 4  # IP头部长度（字节）
                esp_header_len = len(enc_esp) - len(enc_esp.data)  # ESP头部长度（不含加密数据）

                # ESP层关键参数
                spi = enc_esp.spi  # 安全参数索引
                seq = enc_esp.seq  # 序列号
                iv = bytes(enc_esp.data[:16])  # 初始化向量（前16字节）
                icv = bytes(enc_esp.data[-12:])  # 完整性校验值（最后12字节）
                encrypted_data_length = len(enc_esp.data)  # 加密数据总长度（包括payload、填充、padlen、nexthead、ICV）
                encrypted_head_length = data_len - encrypted_data_length  # 加密数据头部长度 esp头（8）+ip头（20）+数据链路层头(14)

                # === 明文包特征提取 ===
                if not IP in pkt_dec:
                    print(f"明文包缺少IP层，跳过：{pkt_dec.summary()}")
                    continue

                dec_ip = pkt_dec[IP]
                transport_layer = pkt_dec[TCP] if TCP in pkt_dec else pkt_dec[UDP] if UDP in pkt_dec else None

                # 明文协议头长度计算
                ip_hdr = dec_ip.ihl * 4  # IP头部长度
                transport_hdr = 0
                if TCP in pkt_dec:
                    transport_hdr = pkt_dec[TCP].dataofs * 4  # TCP头部长度
                elif UDP in pkt_dec:
                    transport_hdr = 8  # UDP头部长度
                plaintext_hdr = ip_hdr + transport_hdr

                # 明文数据负载长度
                plaintext_data_len = len(transport_layer.payload) if transport_layer else 0
                plaintext_data_len = max(plaintext_data_len, 0)  # 防止负数

                # 明文总长度（头部+负载）
                plaintext_total = plaintext_hdr + plaintext_data_len

                # 计算填充长度（加密数据长度 - (IV + 明文总长度 + 填充字段长度、下一头部（2字节） + ICV)）
                padding_length = encrypted_data_length - (16 + plaintext_total + 2 + 12)
                padding_length = max(padding_length, 0)  # 防止负数

                # === 解密包处理（分片重组） ===
                # 处理包并获取分片结果
                processor_result = processor.process_packet(pkt_dec)

                # 获取分片信息
                group_info = processor.get_current_group_info(pkt_dec)
                complete_id = group_info.get("complete_id")
                total_length = group_info.get("total_length")

                # === 构建特征行 ===
                row = [
                    enc_time,  # 时间戳
                    spi,  # 安全参数索引
                    seq,  # 序列号
                    iv,  # 初始化向量（bytes类型）
                    icv,  # 完整性校验值（bytes类型）
                    data_len,  # 数据链路层总长度
                    encrypted_head_length,  # 加密数据头部长度 esp头（8）+ip头（20）+数据链路层头(14)
                    encrypted_data_length,  # 加密协议体数据长度
                    plaintext_hdr,  # 明文协议头部长度
                    plaintext_data_len,  # 明文数据体长度
                    plaintext_total,  # 明文总长度
                    padding_length,  # 填充长度
                    complete_id,  # 分片重组ID
                    total_length  # 分片重组后的总长度（未重组完记为*）
                ]

                data.append(row)

            except Exception as e:
                print(f"处理包失败：{str(e)}，跳过此包")

        # === 特征输出 ===
        # 定义所有特征列名
        columns = [
            "timestamp",  # 时间戳
            "spi",  # 安全参数索引
            "sequence_number",  # 序列号
            "initialization_vector",  # IV
            "integrity_check_value",  # ICV
            "encrypted_total_length",  # 加密数据总长度
            "encrypted_head_length",  # 加密数据头部长度 esp头（8）+ip头（20）+数据链路层头(14)
            "encrypted_data_length",  # 加密协议体数据长度
            "plaintext_header_length",  # 明文协议头部长度
            "plaintext_data_length",  # 明文数据体长度
            "plaintext_total_length",  # 明文总长度
            "padding_length",  # 填充长度
            "complete_id",  # 分片重组ID
            "total_length"  # 分片重组后的总长度（未重组完记为*）
        ]

        if data:
            # 创建DataFrame并保存
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(output_path, index=False, sep="|")
            print(f"特征文件已保存：{output_path}")
        else:
            print(f"无有效数据：{output_path}")

# 主执行流程
if __name__ == "__main__":
    for category in CATEGORIES:
        process_category(category)