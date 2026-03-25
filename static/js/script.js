document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    const errorText = document.getElementById('errorText');
    const statusText = document.getElementById('statusText');

    // 模拟处理步骤
    const processSteps = [
        "正在加载模型...",
        "解析PCAP文件...",
        "提取网络特征...",
        "执行长度预测...",
        "生成分析报告..."
    ];

    // 点击按钮触发文件选择
    uploadBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        fileInput.click();
    });

    // 文件选择变化
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    // 拖拽相关事件
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    // 处理拖放文件
    dropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFiles(files);
        }
    });

    // 处理上传的文件
    function handleFiles(files) {
        const file = files[0];

        if (!file.name.endsWith('.pcap')) {
            showError('请上传.pcap格式的文件');
            return;
        }

        if (file.size > 50 * 1024 * 1024) { // 50MB限制
            showError('文件大小超过50MB限制');
            return;
        }

        // 显示加载状态
        startLoadingAnimation();
        resultsDiv.style.display = 'none';
        errorDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`服务器错误: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            stopLoadingAnimation();

            if (data.error) {
                showError(data.error);
                return;
            }

            // 显示结果
            document.getElementById('featuresContent').textContent = data.features;
            document.getElementById('predictionsContent').textContent = data.predictions;

            // 设置下载链接
            document.getElementById('downloadFeatures').href = `/output/${encodeURIComponent(file.name.split('.')[0])}/${encodeURIComponent(data.features_filename)}`;
            document.getElementById('downloadPredictions').href = `/output/${encodeURIComponent(file.name.split('.')[0])}/${encodeURIComponent(data.predictions_filename)}`;

            resultsDiv.style.display = 'block';

            // 结果显示动画
            setTimeout(() => {
                resultsDiv.style.opacity = '1';
                resultsDiv.style.transform = 'translateY(0)';
            }, 50);
        })
        .catch(error => {
            stopLoadingAnimation();
            showError('处理文件时出错: ' + error.message);
        });
    }

    function startLoadingAnimation() {
        loadingDiv.style.display = 'block';
        loadingDiv.style.opacity = '0';
        loadingDiv.style.transform = 'translateY(20px)';
        loadingDiv.style.transition = 'all 0.3s ease-out';

        setTimeout(() => {
            loadingDiv.style.opacity = '1';
            loadingDiv.style.transform = 'translateY(0)';
        }, 50);

        // 模拟处理步骤
        let step = 0;
        const interval = setInterval(() => {
            statusText.textContent = processSteps[step];
            step = (step + 1) % processSteps.length;
        }, 2000);

        window.loadingInterval = interval;
    }

    function stopLoadingAnimation() {
        loadingDiv.style.opacity = '0';
        loadingDiv.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            loadingDiv.style.display = 'none';
            clearInterval(window.loadingInterval);
        }, 300);
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
});