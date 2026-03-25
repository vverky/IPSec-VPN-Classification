from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import model_prediction as predict
from flask import send_from_directory
import traceback
# 初始化Flask应用
app = Flask(__name__)
# 配置上传文件夹和最大文件大小
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传16MB

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 主页路由 - 渲染index.html模板
@app.route('/')
def index():
    return render_template('index.html')
# 文件下载路由
@app.route('/output/<path:filename>')
def download_file(filename):
    return send_from_directory('output', filename)
# 文件上传处理路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pcap'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 调用你的预测函数
            csv_path, pred_path = predict.process_pcap(filepath)

            # 读取结果文件内容
            with open(csv_path, 'r') as f:
                features_content = f.read()

            with open(pred_path, 'r') as f:
                predictions_content = f.read()

            return jsonify({
                'success': True,
                'features': features_content,
                'predictions': predictions_content,
                'features_filename': os.path.basename(csv_path),
                'predictions_filename': os.path.basename(pred_path)
            })
        except Exception as e:
            print("服务器内部错误：", str(e))
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only .pcap files are allowed.'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)