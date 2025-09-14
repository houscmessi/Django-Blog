FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 系统依赖（Pillow 等可能用到）
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 迁移（Render 上也会再执行一次，双保险）
RUN python manage.py migrate --noinput || true

EXPOSE 8000
CMD ["gunicorn","mysite.wsgi:application","-b","0.0.0.0:8000"]