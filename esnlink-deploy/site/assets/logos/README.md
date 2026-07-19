# 客户 Logo 资源

## 当前状态

使用自动生成的 **行业示意 SVG**（单字母标识 + 企业名称），非官方商标。

## 替换为真实 Logo

将客户授权 Logo 文件放入此目录，保持文件名一致即可自动生效：

| 文件 | 对应客户 |
|------|----------|
| `telecom-ct.svg` | 中国电信 |
| `telecom-cm.svg` | 中国移动 |
| `telecom-cu.svg` | 中国联通 |
| `satellite.svg` | 中国星网 |
| `finance.svg` | 城商行联盟 |
| `education.svg` | 职教集团 |
| `ecommerce.svg` | 头部电商 |
| `healthcare.svg` | 社区医院 |

支持格式：SVG（推荐）、PNG（透明背景，高度 64px+）

重新生成示意 Logo：`python3 generate_logos.py`
