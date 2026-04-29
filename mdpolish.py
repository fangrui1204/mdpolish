from openai import OpenAI
import sys
import os
from pathlib import Path

client = OpenAI(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

SYSTEM_PROMPT = """你是一个 Markdown 笔记整理助手。任务是把用户给的杂乱笔记整理得结构清晰、术语统一、可读性强。
规则：
1. 保留原作者的核心内容和表达习惯，不改写风格
2. 修正明显的标题层级混乱（如全是 # 或全无标题）
3. 统一术语和人称
4. 修正明显病句和错别字
5. 必要时补充段落过渡句
6. 输出纯 Markdown，不要解释说明"""


def polish_markdown(text: str):
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        max_tokens=8000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    content = response.choices[0].message.content
    usage = response.usage
    return content, usage


def main():
    if len(sys.argv) < 2:
        print("用法: python mdpolish.py <文件路径>")
        return
    path = Path(sys.argv[1])
    backup_path = path.with_suffix(path.suffix + ".bak")
    backup_path.write_bytes(path.read_bytes())
    text = path.read_text(encoding="utf-8-sig")
    polished, usage = polish_markdown(text)
    out_path = path.with_stem(path.stem + ".polished")
    out_path.write_text(polished, encoding="utf-8")
    print(f"已输出: {out_path}")
    print(f"Token 用量: 输入={usage.prompt_tokens}, 输出={usage.completion_tokens}")


if __name__ == "__main__":
    main()
