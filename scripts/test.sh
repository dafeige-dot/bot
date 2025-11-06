#!/bin/bash

# 测试脚本

echo "运行测试..."

# 运行pytest
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

echo "测试完成！"
echo "查看覆盖率报告: htmlcov/index.html"

