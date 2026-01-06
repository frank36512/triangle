"""
接口配置初始化脚本
快速配置多个API接口用于测试
"""
from src.utils.config import Config

def init_demo_apis():
    """初始化演示接口"""
    config = Config()
    
    print("开始配置演示接口...")
    
    # 配置LLM接口
    print("\n1. 配置LLM接口")
    config.add_llm_api(
        name="OpenAI主账号",
        provider="openai",
        api_key="sk-your-openai-key",  # 请替换为真实的API密钥
        base_url="https://api.openai.com/v1/chat/completions",
        model="gpt-4o"
    )
    print("  ✓ OpenAI主账号")
    
    config.add_llm_api(
        name="DeepSeek备用",
        provider="deepseek",
        api_key="sk-your-deepseek-key",  # 请替换为真实的API密钥
        base_url="https://api.deepseek.com",
        model="deepseek-chat"
    )
    print("  ✓ DeepSeek备用")
    
    config.set_default_llm_api("OpenAI主账号")
    print("  → 默认: OpenAI主账号")
    
    # 配置图片接口
    print("\n2. 配置图片生成接口")
    config.add_image_api(
        name="Flux Pro主接口",
        provider="flux",
        api_key="your-flux-key",  # 请替换为真实的API密钥
        base_url="",
        model="flux-pro"
    )
    print("  ✓ Flux Pro主接口")
    
    config.add_image_api(
        name="DALL-E备用",
        provider="openai",
        api_key="sk-your-openai-key",  # 请替换为真实的API密钥
        base_url="",
        model="dall-e-3"
    )
    print("  ✓ DALL-E备用")
    
    config.set_default_image_api("Flux Pro主接口")
    print("  → 默认: Flux Pro主接口")
    
    # 配置视频接口
    print("\n3. 配置视频生成接口")
    config.add_video_api(
        name="Luma Dream主接口",
        provider="luma",
        api_key="your-luma-key",  # 请替换为真实的API密钥
        base_url="",
        model="luma-1.6"
    )
    print("  ✓ Luma Dream主接口")
    
    config.add_video_api(
        name="Runway Gen-3备用",
        provider="runway",
        api_key="your-runway-key",  # 请替换为真实的API密钥
        base_url="",
        model="gen-3"
    )
    print("  ✓ Runway Gen-3备用")
    
    config.set_default_video_api("Luma Dream主接口")
    print("  → 默认: Luma Dream主接口")
    
    # 保存配置
    config.save()
    print("\n✅ 配置已保存到 data/config.json")
    
    # 显示配置摘要
    print("\n" + "="*50)
    print("配置摘要:")
    print("="*50)
    print(f"\nLLM接口数量: {len(config.get_llm_apis())}")
    for api in config.get_llm_apis():
        default_mark = " [默认]" if api["name"] == config.get_default_llm_api() else ""
        print(f"  • {api['name']}{default_mark} ({api['provider']})")
    
    print(f"\n图片接口数量: {len(config.get_image_apis())}")
    for api in config.get_image_apis():
        default_mark = " [默认]" if api["name"] == config.get_default_image_api() else ""
        print(f"  • {api['name']}{default_mark} ({api['provider']})")
    
    print(f"\n视频接口数量: {len(config.get_video_apis())}")
    for api in config.get_video_apis():
        default_mark = " [默认]" if api["name"] == config.get_default_video_api() else ""
        print(f"  • {api['name']}{default_mark} ({api['provider']})")
    
    print("\n" + "="*50)
    print("提示: 请在配置文件中替换为真实的API密钥")
    print("配置文件位置: data/config.json")
    print("="*50)

if __name__ == "__main__":
    init_demo_apis()
