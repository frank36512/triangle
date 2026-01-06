
HELP_CONTENT = {
    "zh": {
        "guide": """
        <html>
        <head>
            <style>
                body { font-family: '微软雅黑', Arial; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                h3 { color: #059669; margin-top: 20px; }
                .step { background-color: #f0f9ff; padding: 12px; margin: 10px 0; border-left: 4px solid #2563eb; }
                .tip { background-color: #fef3c7; padding: 10px; margin: 10px 0; border-radius: 6px; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
            </style>
        </head>
        <body>
            <h2>📖 AI广告视频生成系统 - 使用指南</h2>
            
            <h3>🎯 基本流程</h3>
            <div class="step">
                <strong>1. 创建项目</strong><br>
                点击左侧"新建项目"按钮，填写项目基本信息
            </div>
            
            <div class="step">
                <strong>2. 生成提示词</strong><br>
                在"提示词生成"面板，选择LLM接口，点击"生成提示词"
            </div>
            
            <div class="step">
                <strong>3. 生成分镜图片</strong><br>
                在"分镜图片"面板，选择图片生成接口，点击"生成所有分镜"
            </div>
            
            <div class="step">
                <strong>4. 生成视频</strong><br>
                在"视频生成"面板，选择视频生成接口，点击"生成视频"
            </div>
            
            <h3>💡 使用技巧</h3>
            <ul>
                <li><strong>参考图片：</strong>上传产品或场景图片，AI会参考这些图片生成更贴合的内容</li>
                <li><strong>核心卖点：</strong>清晰描述产品特点，有助于生成更精准的提示词</li>
                <li><strong>风格选择：</strong>根据目标受众选择合适的视频风格</li>
                <li><strong>分镜编辑：</strong>生成的分镜图片可以单独重新生成或替换</li>
            </ul>
            
            <div class="tip">
                <strong>💰 费用提示：</strong>生成提示词、分镜图片和视频都会调用相应的API接口，产生费用。
                建议先配置好各个接口，测试无误后再批量生成。
            </div>
            
            <h3>⚙️ 接口配置</h3>
            <p>在"系统设置"面板中配置：</p>
            <ul>
                <li><strong>LLM API：</strong>用于生成提示词（支持OpenAI、DeepSeek等）</li>
                <li><strong>图片生成API：</strong>用于生成分镜图片</li>
                <li><strong>视频生成API：</strong>用于生成最终视频</li>
            </ul>
            
            <h3>📁 项目管理</h3>
            <ul>
                <li>所有项目数据保存在 <code>projects</code> 目录</li>
                <li>每个项目包含：基本信息、提示词、分镜图片、生成的视频</li>
                <li>删除项目会同时删除所有相关文件，请谨慎操作</li>
            </ul>
        </body>
        </html>
        """,
        "shortcuts": """
        <html>
        <head>
            <style>
                body { font-family: '微软雅黑', Arial; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background-color: #2563eb; color: white; padding: 12px; text-align: left; }
                td { padding: 10px; border-bottom: 1px solid #e5e7eb; }
                tr:hover { background-color: #f8fafc; }
                .key { background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; 
                       font-family: 'Courier New', monospace; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>⌨️ 快捷键说明</h2>
            
            <table>
                <tr>
                    <th>功能</th>
                    <th>快捷键</th>
                    <th>说明</th>
                </tr>
                <tr>
                    <td>新建项目</td>
                    <td><span class="key">Ctrl+N</span></td>
                    <td>快速创建新项目</td>
                </tr>
                <tr>
                    <td>刷新列表</td>
                    <td><span class="key">F5</span></td>
                    <td>刷新项目列表</td>
                </tr>
                <tr>
                    <td>项目信息</td>
                    <td><span class="key">Alt+1</span></td>
                    <td>切换到项目信息面板</td>
                </tr>
                <tr>
                    <td>提示词生成</td>
                    <td><span class="key">Alt+2</span></td>
                    <td>切换到提示词生成面板</td>
                </tr>
                <tr>
                    <td>分镜图片</td>
                    <td><span class="key">Alt+3</span></td>
                    <td>切换到分镜图片面板</td>
                </tr>
                <tr>
                    <td>视频生成</td>
                    <td><span class="key">Alt+4</span></td>
                    <td>切换到视频生成面板</td>
                </tr>
                <tr>
                    <td>系统设置</td>
                    <td><span class="key">Alt+5</span></td>
                    <td>切换到系统设置面板</td>
                </tr>
                <tr>
                    <td>帮助</td>
                    <td><span class="key">F1</span></td>
                    <td>打开帮助面板</td>
                </tr>
            </table>
        </body>
        </html>
        """,
        "about": """
        <html>
        <head>
            <style>
                body { font-family: '微软雅黑', Arial; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                .info { background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .version { font-size: 24px; color: #2563eb; font-weight: bold; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
            </style>
        </head>
        <body>
            <h2>ℹ️ 关于</h2>
            
            <div class="info">
                <p class="version">AI广告视频生成系统 v1.0.0</p>
                <p>一款基于AI技术的广告视频自动生成工具</p>
            </div>
            
            <h3>✨ 主要功能</h3>
            <ul>
                <li>AI智能生成视频脚本提示词</li>
                <li>自动生成9宫格分镜图片</li>
                <li>一键生成完整广告视频</li>
                <li>支持多种AI接口（OpenAI、DeepSeek、Sora等）</li>
                <li>项目管理和历史记录</li>
            </ul>
            
            <h3>🛠️ 技术栈</h3>
            <ul>
                <li>Python 3.11+</li>
                <li>PyQt6 - 现代化GUI框架</li>
                <li>OpenAI API - 大语言模型</li>
                <li>图片生成API - AI图片生成</li>
                <li>视频生成API - AI视频生成</li>
            </ul>
            
            <h3>📄 许可证</h3>
            <p>本软件仅供学习和研究使用</p>
            
            <h3>📮 联系方式</h3>
            <p>如有问题或建议，欢迎反馈</p>
        </body>
        </html>
        """
    },
    "en": {
        "guide": """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                h3 { color: #059669; margin-top: 20px; }
                .step { background-color: #f0f9ff; padding: 12px; margin: 10px 0; border-left: 4px solid #2563eb; }
                .tip { background-color: #fef3c7; padding: 10px; margin: 10px 0; border-radius: 6px; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
            </style>
        </head>
        <body>
            <h2>📖 AI Ad Video Generator - User Guide</h2>
            
            <h3>🎯 Basic Workflow</h3>
            <div class="step">
                <strong>1. Create Project</strong><br>
                Click "New Project" on the left, fill in basic info.
            </div>
            
            <div class="step">
                <strong>2. Generate Prompts</strong><br>
                In "Prompts" panel, select LLM API, click "Generate Prompts".
            </div>
            
            <div class="step">
                <strong>3. Generate Storyboards</strong><br>
                In "Storyboards" panel, select Image API, click "Generate All".
            </div>
            
            <div class="step">
                <strong>4. Generate Video</strong><br>
                In "Video Gen" panel, select Video API, click "Generate Video".
            </div>
            
            <h3>💡 Tips</h3>
            <ul>
                <li><strong>Reference Images:</strong> Upload product images for better consistency.</li>
                <li><strong>Selling Points:</strong> Clear description helps generate better prompts.</li>
                <li><strong>Style:</strong> Choose style based on target audience.</li>
                <li><strong>Editing:</strong> You can regenerate individual storyboard images.</li>
            </ul>
            
            <div class="tip">
                <strong>💰 Cost Warning:</strong> Generating prompts, images, and videos consumes API credits.
                Configure APIs correctly and test before batch generation.
            </div>
            
            <h3>⚙️ Configuration</h3>
            <p>Configure in "Settings" panel:</p>
            <ul>
                <li><strong>LLM API:</strong> For prompt generation (OpenAI, DeepSeek, etc.)</li>
                <li><strong>Image API:</strong> For storyboard generation</li>
                <li><strong>Video API:</strong> For final video generation</li>
            </ul>
            
            <h3>📁 Project Management</h3>
            <ul>
                <li>All data saved in <code>projects</code> directory.</li>
                <li>Deleting a project removes all associated files permanently.</li>
            </ul>
        </body>
        </html>
        """,
        "shortcuts": """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background-color: #2563eb; color: white; padding: 12px; text-align: left; }
                td { padding: 10px; border-bottom: 1px solid #e5e7eb; }
                tr:hover { background-color: #f8fafc; }
                .key { background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; 
                       font-family: 'Courier New', monospace; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>⌨️ Shortcuts</h2>
            
            <table>
                <tr>
                    <th>Function</th>
                    <th>Shortcut</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>New Project</td>
                    <td><span class="key">Ctrl+N</span></td>
                    <td>Create new project</td>
                </tr>
                <tr>
                    <td>Refresh List</td>
                    <td><span class="key">F5</span></td>
                    <td>Refresh project list</td>
                </tr>
                <tr>
                    <td>Project Info</td>
                    <td><span class="key">Alt+1</span></td>
                    <td>Switch to Project Info</td>
                </tr>
                <tr>
                    <td>Prompts</td>
                    <td><span class="key">Alt+2</span></td>
                    <td>Switch to Prompts</td>
                </tr>
                <tr>
                    <td>Storyboards</td>
                    <td><span class="key">Alt+3</span></td>
                    <td>Switch to Storyboards</td>
                </tr>
                <tr>
                    <td>Video Gen</td>
                    <td><span class="key">Alt+4</span></td>
                    <td>Switch to Video Gen</td>
                </tr>
                <tr>
                    <td>Settings</td>
                    <td><span class="key">Alt+5</span></td>
                    <td>Switch to Settings</td>
                </tr>
                <tr>
                    <td>Help</td>
                    <td><span class="key">F1</span></td>
                    <td>Open Help</td>
                </tr>
            </table>
        </body>
        </html>
        """,
        "about": """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.8; padding: 20px; }
                h2 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
                .info { background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .version { font-size: 24px; color: #2563eb; font-weight: bold; }
                ul { margin-left: 20px; }
                li { margin: 8px 0; }
            </style>
        </head>
        <body>
            <h2>ℹ️ About</h2>
            
            <div class="info">
                <p class="version">AI Ad Video Generator v1.0.0</p>
                <p>AI-powered automatic advertising video generation tool</p>
            </div>
            
            <h3>✨ Key Features</h3>
            <ul>
                <li>AI script and prompt generation</li>
                <li>Automatic 9-grid storyboard generation</li>
                <li>One-click video generation</li>
                <li>Multi-model support (OpenAI, DeepSeek, Sora, etc.)</li>
                <li>Project management and history</li>
            </ul>
            
            <h3>🛠️ Tech Stack</h3>
            <ul>
                <li>Python 3.11+</li>
                <li>PyQt6 - Modern GUI Framework</li>
                <li>OpenAI API - LLM</li>
                <li>Image Gen API</li>
                <li>Video Gen API</li>
            </ul>
            
            <h3>📄 License</h3>
            <p>For educational and research purposes only.</p>
            
            <h3>📮 Contact</h3>
            <p>Feedback welcome!</p>
        </body>
        </html>
        """
    }
}
