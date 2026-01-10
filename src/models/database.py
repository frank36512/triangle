"""
数据库管理模块
"""
import sqlite3
import os
import sys
import json
from datetime import datetime
from typing import List, Optional
from .project import Project


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            # Use current working directory or deduce from file path
            # Using "." relies on CWD, which is usually fine if run via script
            base_dir = "."
            
        if db_path is None:
            self.db_path = os.path.join(base_dir, "data", "projects.db")
        else:
            self.db_path = db_path
            
        self.projects_dir = os.path.join(base_dir, "projects")
        self._init_database()
        
    def _init_database(self):
        """初始化数据库和表结构"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建项目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            product_name TEXT,
            company_name TEXT,
            target_audience TEXT,
            duration INTEGER,
            style TEXT,
            keywords TEXT,
            frame_prompts TEXT,
            video_prompt TEXT,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reference_image TEXT
        )
        ''')
        
        # 检查并添加 reference_image 列（如果不存在）
        cursor.execute("PRAGMA table_info(projects)")
        columns = [info[1] for info in cursor.fetchall()]
        if "reference_image" not in columns:
            try:
                cursor.execute("ALTER TABLE projects ADD COLUMN reference_image TEXT")
                print("已添加 reference_image 列到数据库")
            except Exception as e:
                print(f"添加 reference_image 列失败: {e}")
                
        # 检查并添加 video_segments 列（如果不存在）
        if "video_segments" not in columns:
            try:
                cursor.execute("ALTER TABLE projects ADD COLUMN video_segments TEXT")
                print("已添加 video_segments 列到数据库")
            except Exception as e:
                print(f"添加 video_segments 列失败: {e}")
        
        conn.commit()
        conn.close()
    
    def create_project(self, project: Project) -> int:
        """创建新项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO projects (name, type, product_name, company_name, 
                            target_audience, duration, style, keywords,
                            frame_prompts, video_prompt, reference_image, video_segments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project.name,
            project.type,
            project.product_name,
            project.company_name,
            project.target_audience,
            project.duration,
            project.style,
            project.keywords,
            json.dumps(project.frame_prompts, ensure_ascii=False),
            project.video_prompt,
            project.reference_image,
            json.dumps(project.video_segments, ensure_ascii=False)
        ))
        
        project_id = cursor.lastrowid
        
        # 创建项目专属文件夹
        project_path = os.path.join(self.projects_dir, str(project_id))
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "frames"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "video"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "reference"), exist_ok=True)
        
        conn.commit()
        conn.close()
        
        return project_id
    
    def update_project(self, project: Project):
        """更新项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE projects 
        SET name=?, type=?, product_name=?, company_name=?, 
            target_audience=?, duration=?, style=?, keywords=?,
            frame_prompts=?, video_prompt=?, update_time=?, reference_image=?, video_segments=?,
            voice_tone=?, voice_speed=?
        WHERE id=?
        ''', (
            project.name,
            project.type,
            project.product_name,
            project.company_name,
            project.target_audience,
            project.duration,
            project.style,
            project.keywords,
            json.dumps(project.frame_prompts, ensure_ascii=False),
            project.video_prompt,
            datetime.now(),
            project.reference_image,
            json.dumps(project.video_segments, ensure_ascii=False),
            project.voice_tone,
            project.voice_speed,
            project.id
        ))
        
        conn.commit()
        conn.close()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """获取单个项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id=?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_project(row)
        return None
    
    def get_all_projects(self) -> List[Project]:
        """获取所有项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects ORDER BY create_time DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_project(row) for row in rows]
    
    def delete_project(self, project_id: int):
        """删除项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
        conn.commit()
        conn.close()
        
        # 删除项目文件夹
        import shutil
        project_path = os.path.join(self.projects_dir, str(project_id))
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
    
    def _row_to_project(self, row) -> Project:
        """将数据库行转换为Project对象"""
        # 处理可能缺少的reference_image列（向后兼容）
        reference_image = ""
        if len(row) > 13:
            reference_image = row[13] or ""
            
        # 处理可能缺少的video_segments列
        video_segments = []
        if len(row) > 14:
            try:
                video_segments = json.loads(row[14]) if row[14] else []
            except:
                video_segments = []
        
        # 处理可能缺少的voice_tone和voice_speed列
        voice_tone = "沉稳男声"
        voice_speed = "适中(120字/分钟)"
        if len(row) > 15:
            voice_tone = row[15] or "沉稳男声"
        if len(row) > 16:
            voice_speed = row[16] or "适中(120字/分钟)"
            
        project = Project(
            id=row[0],
            name=row[1],
            type=row[2],
            product_name=row[3],
            company_name=row[4],
            target_audience=row[5],
            duration=row[6],
            style=row[7],
            keywords=row[8],
            frame_prompts=json.loads(row[9]) if row[9] else [],
            video_prompt=row[10] or "",
            create_time=datetime.fromisoformat(row[11]) if row[11] else None,
            update_time=datetime.fromisoformat(row[12]) if row[12] else None,
            reference_image=reference_image,
            video_segments=video_segments,
            voice_tone=voice_tone,
            voice_speed=voice_speed
        )
        return project
    
    def get_project_path(self, project_id: int) -> str:
        """获取项目文件夹路径"""
        return os.path.join(self.projects_dir, str(project_id))
