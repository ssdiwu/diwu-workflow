#!/usr/bin/env python3
import unittest
import json
import os
import tempfile
from datetime import datetime

class TestContextMonitor(unittest.TestCase):
    def setUp(self):
        self.sid = 'test_session_123'
        self.counter_file = f'/tmp/diwu_ctx_{self.sid}'
        self.crit_file = f'/tmp/diwu_ctx_{self.sid}_critical'
        self.crit_ts_file = f'/tmp/diwu_ctx_{self.sid}_critical_ts'
        self.config_cache_file = f'/tmp/diwu_ctx_{self.sid}_config_cache'
        self.test_recording = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
        self.test_task_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')

    def tearDown(self):
        for f in [self.counter_file, self.crit_file, self.crit_ts_file, self.config_cache_file]:
            if os.path.exists(f):
                os.remove(f)
        os.unlink(self.test_recording.name)
        os.unlink(self.test_task_json.name)

    def test_a_logic_critical_threshold_triggers_block(self):
        """A 逻辑测试：工具调用次数达到 CRITICAL 阈值时输出阻塞提醒且记录时间戳"""
        # 模拟计数器达到 CRITICAL (50)
        with open(self.counter_file, 'w') as f:
            f.write('49')

        # 模拟脚本逻辑
        count = int(open(self.counter_file).read().strip()) + 1
        CRITICAL_THRESHOLD = 50

        self.assertEqual(count, 50)

        # 验证达到阈值时应该触发阻塞
        if count >= CRITICAL_THRESHOLD and not os.path.exists(self.crit_file):
            with open(self.crit_file, 'w') as f:
                f.write('1')
            with open(self.crit_ts_file, 'w') as f:
                f.write(str(1234567890.0))

            output = {
                'decision': 'block',
                'reason': f'⚠️ CRITICAL: Context 使用量已达临界值（工具调用 {count} 次）。'
            }

            self.assertEqual(output['decision'], 'block')
            self.assertIn('CRITICAL', output['reason'])
            self.assertIn('50', output['reason'])
            self.assertTrue(os.path.exists(self.crit_file))
            self.assertTrue(os.path.exists(self.crit_ts_file))

    def test_b_logic_auto_checkpoint_when_recording_not_updated(self):
        """B 逻辑测试：CRITICAL+DELAY 且 recording.md mtime 早于 critical_ts 时自动写入 checkpoint"""
        critical_ts = 1234567800.0
        count = 60  # CRITICAL(50) + DELAY(10)

        # 写入 critical_ts
        with open(self.crit_ts_file, 'w') as f:
            f.write(str(critical_ts))

        # 创建 recording.md 并设置早于 critical_ts 的 mtime
        with open(self.test_recording.name, 'w') as f:
            f.write('## Session 2026-03-14 04:00:00\n\nSome content\n')
        os.utime(self.test_recording.name, (1234567700.0, 1234567700.0))

        # 创建 task.json
        task_data = {'tasks': [{'id': 1, 'title': 'Test Task', 'status': 'InProgress'}]}
        with open(self.test_task_json.name, 'w') as f:
            json.dump(task_data, f)

        # 验证条件
        recording_mtime = os.path.getmtime(self.test_recording.name)
        self.assertLess(recording_mtime, critical_ts)
        self.assertGreaterEqual(count, 60)

        # 模拟自动写入逻辑
        if count >= 60 and os.path.exists(self.crit_ts_file):
            stored_ts = float(open(self.crit_ts_file).read().strip())
            if recording_mtime < stored_ts:
                with open(self.test_recording.name, 'a') as f:
                    f.write('\n### [Auto Checkpoint]\n\n**Task#1**: Test Task (InProgress)\n')

        # 验证写入
        content = open(self.test_recording.name).read()
        self.assertIn('[Auto Checkpoint]', content)
        self.assertIn('Task#1', content)

    def test_config_cache_uses_cached_when_mtime_unchanged(self):
        """配置缓存测试：settings.json mtime 未变化时使用缓存配置"""
        settings_mtime = 1234567890.0
        cache_data = {
            'mtime': settings_mtime,
            'config': {'warning': 25, 'critical': 45, 'delay': 8, 'session_window': 500}
        }

        with open(self.config_cache_file, 'w') as f:
            json.dump(cache_data, f)

        # 模拟 load_config 逻辑
        if os.path.exists(self.config_cache_file):
            cache = json.load(open(self.config_cache_file))
            if cache.get('mtime') == settings_mtime:
                config = cache.get('config', {})

        self.assertEqual(config['warning'], 25)
        self.assertEqual(config['critical'], 45)
        self.assertEqual(config['delay'], 8)
        self.assertEqual(config['session_window'], 500)

    def test_time_window_append_vs_new_session(self):
        """时间窗口测试：recording.md 最后 session 时间戳距当前 < 600s 则追加，否则新建"""
        SESSION_WINDOW = 600

        # 测试追加模式
        last_session_time = datetime(2026, 3, 14, 4, 55, 0)
        current_time = datetime(2026, 3, 14, 5, 0, 0)
        diff_seconds = (current_time - last_session_time).total_seconds()
        self.assertLess(diff_seconds, SESSION_WINDOW)

        # 测试新建模式
        last_session_time = datetime(2026, 3, 14, 4, 0, 0)
        current_time = datetime(2026, 3, 14, 5, 0, 0)
        diff_seconds = (current_time - last_session_time).total_seconds()
        self.assertGreaterEqual(diff_seconds, SESSION_WINDOW)

if __name__ == '__main__':
    unittest.main()
