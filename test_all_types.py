# -*- coding: utf-8 -*-
from src.mcp_service import MCPDataCleaningService

r = MCPDataCleaningService.get_supported_business_types()
print(f"\n支持的业务类型总数: {r['data']['count']}\n")
print("=" * 60)

for i, bt in enumerate(r['data']['business_types'], 1):
    print(f"{i:2d}. {bt['business_type_id']:15s} - {bt['name']:20s} ({bt['table_name']})")

print("=" * 60)
print(f"\n✅ 全部 {r['data']['count']} 个业务类型已注册并可用！\n")
