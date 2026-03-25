from scapy.all import *          # 导入 Scapy，用于解析和构造网络数据包
from Crypto.Cipher import AES    # 导入 AES 加密算法模块
from Crypto.Hash import HMAC, SHA1  # 验证数据完整性
import binascii                  # 用于十六进制字符串与字节的转换

INPUT_DIR = "IPSecVPN_traffic"
# 密钥配置
spi_to_keys = {
    0xc02f725e: {
        "enc_key": binascii.unhexlify("7e5b45c846dfeaa4022d565e84c8823c"),
        "auth_key": binascii.unhexlify("aaafdde152e48e474100f97681fc78f30e1ca4aa"),
    },
    0xce4feb28: {
        "enc_key": binascii.unhexlify("feb5cff6fc95770bfb29386f81b72221"),
        "auth_key": binascii.unhexlify("ee575a13f2463c72caa7fd310795bebfa5327e64"),
    },
}

def decrypt_esp_packet(pkt):
    if not pkt.haslayer(ESP):
        return None

    esp_layer = pkt[ESP]       # 提取ESP层
    spi = esp_layer.spi        # 提取spi
    esp_full = bytes(esp_layer)     # 提取整个ESP层的原始字节

    if len(esp_full) < 12:
        print(f"[!] 数据包长度不足，跳过解密 (SPI={hex(spi)})")
        return None

    # 分割 HMAC 和数据
    icv = esp_full[-12:]     # 最后12字节是 HMAC
    data_to_verify = esp_full[:-12]   # 前面的数据用于计算 HMAC
    # 验证密文长度
    iv = esp_full[8:24]
    ciphertext = esp_full[24:-12]

    # 获取密钥
    if spi not in spi_to_keys:
        # print(f"[!] 未找到 SPI={hex(spi)} 的密钥，跳过解密")
        return None
    enc_key = spi_to_keys[spi]["enc_key"]
    auth_key = spi_to_keys[spi]["auth_key"]

    # 验证 HMAC
    if not verify_hmac(auth_key, data_to_verify, icv):
        # print(f"[!] HMAC 验证失败，返回原数据包")
        return None

    # 验证密文长度
    if len(ciphertext) % AES.block_size != 0:
        # print(f"[!] 密文长度 {len(ciphertext)} 不是 16 的倍数，SPI={hex(spi)}")
        return None

    # AES-CBC 解密
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(ciphertext)

    # 剥离填充和下一头部
    # 留下真正的有效负载
    padding_length = decrypted_data[-2]   # 读取填充长度
    effective_length = len(decrypted_data) - padding_length - 2 # 获取有效负载长度
    effective_data = decrypted_data[:effective_length]

    # 返回解密后的IP包
    # try 块的作用,目的：执行可能存在风险的代码（例如文件操作、网络请求等）。
    try:
        # 解析为一个 IP（IPv4）包，并返回解析后的包对象
        # 在 IPsec 中，ESP（Encapsulating Security Payload）协议会将原始 IP 数据包（如 IPv4 或 IPv6）的负载进行加密，并封装到一个新的外层 IP 包中传输。
        # 解密后，得到的 decrypted_data 理论上应是原始 IP 包的完整内容（包括原始 IP 头部和负载），代码假设是IPV4协议
        ip_pkt = IP(effective_data)
        ip_pkt.time = pkt.time  # <== 复制原始时间戳
        return ip_pkt
    # except 块的作用,目的：捕获并处理 try 块中发生的异常。将异常对象保存到变量 e 中。
    except Exception as e:
        print(f"[!] 解析 IP 失败: {str(e)}, SPI={hex(spi)}")
        return None

# 验证数据的完整性
def verify_hmac(auth_key, data_to_verify, received_hmac):
    hmac_calculated = HMAC.new(auth_key, data_to_verify, digestmod=SHA1)
    computed = hmac_calculated.digest()[:12]  # 取前 12 字节（SHA1 原长 20B）
    return computed == received_hmac  # 比较计算结果与接收到的 HMAC

def main():
    for category in ["web", "im", "ftp"]:
        for num in range(1,201):
            packets = rdpcap(f"{category}/{num}.pcap")
            encrypted_packets = []
            decrypted_packets = []
            for pkt in packets:
                result = decrypt_esp_packet(pkt)
                if result:
                    encrypted_packets.append(pkt)
                    decrypted_packets.append(result)
            wrpcap(f"{category}/decrypted/{num}.pcapng", decrypted_packets)
            wrpcap(f"{category}/encrypted/{num}.pcapng", encrypted_packets)
            print(f"{category}/{num}.pcap解密完成，已保存 {len(decrypted_packets)} 个包")
    print("[+]全部解密完成")

if __name__ == "__main__":
    main()