-- Initialize admin user
INSERT INTO admins (username, password_hash)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qJ9dXz4f0UjKOK')
ON CONFLICT (username) DO NOTHING;

-- Insert sample snake data
INSERT INTO snakes (name, scientific_name, description, temperament, treatment, is_venomous, image)
VALUES
    ('眼镜王蛇', 'Ophiophagus hannah',
     '眼镜王蛇是世界上最大的毒蛇，体长可达5米。它们主要分布在南亚和东南亚地区。',
     '领地意识强，行动敏捷，遇到威胁时会立起身体前部并展开颈部的皮褶',
     '1. 保持冷静，避免恐慌<br>2. 尽快拨打急救电话<br>3. 保持伤口低于心脏位置<br>4. 避免剧烈运动<br>5. 尽快就医',
     true,
     null),
    ('玉米蛇', 'Pantherophis guttatus',
     '玉米蛇是最受欢迎的宠物蛇之一，原产于北美洲。它们性格温顺，体色丰富多变。',
     '性格温顺，很少主动攻击人类，适应能力强',
     '无毒，无需特殊处理。如有咬伤，清洁伤口即可。',
     false,
     null),
    ('竹叶青', 'Trimeresurus stejnegeri',
     '竹叶青是一种小型毒蛇，身体呈翠绿色，常栖息于树枝上。',
     '性格较神经质，容易被惊扰，有领域性',
     '1. 保持冷静<br>2. 尽快就医<br>3. 固定受伤部位<br>4. 避免使用止血带',
     true,
     null),
    ('银环蛇', 'Bungarus multicinctus',
     '银环蛇是中国常见的毒蛇之一，身上有银白色的环纹。虽然体型不大，但毒性很强。',
     '性格胆小，常在夜间活动，一般不主动攻击',
     '1. 立即就医<br>2. 保持静止<br>3. 不要使用止血带或吸毒<br>4. 记录蛇的外观特征',
     true,
     null),
    ('球蟒', 'Python regius',
     '球蟒是最小的蟒蛇之一，因受到惊吓时会缩成一团而得名。它们是非常适合初学者的宠物蛇。',
     '性格温和，较为害羞，喜欢温暖的环境',
     '无毒，非常温顺，一般不会咬人。',
     false,
     null)
ON CONFLICT DO NOTHING;
