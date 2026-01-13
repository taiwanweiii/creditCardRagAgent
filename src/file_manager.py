"""
CSV File Manager for Credit Card Data
Handles timestamped file naming, backup, and cleanup
"""
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import shutil


class CSVFileManager:
    """Manage CSV files with timestamped naming and automatic backup"""
    
    def __init__(self, data_dir: str, backup_dir: str, max_backups: int = 30):
        """
        Initialize CSV file manager
        
        Args:
            data_dir: Directory for current CSV file
            backup_dir: Directory for backup files
            max_backups: Maximum number of backups to keep
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.file_pattern = "信用卡資料模板_*.csv"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create data and backup directories if they don't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directories ensured: {self.data_dir}, {self.backup_dir}")
    
    def get_latest_csv(self) -> Optional[Path]:
        """
        Get the latest CSV file from data directory
        
        Returns:
            Path to the latest CSV file, or None if no files found
        """
        csv_files = sorted(self.data_dir.glob(self.file_pattern))
        
        if not csv_files:
            return None
        
        # Return the latest file (sorted by name, which includes timestamp)
        latest = csv_files[-1]
        print(f"📄 Latest CSV: {latest.name}")
        return latest
    
    def backup_current_csv(self) -> bool:
        """
        Backup current CSV file to backup directory
        
        Returns:
            True if backup successful, False if no file to backup
        """
        current_csv = self.get_latest_csv()
        
        if not current_csv:
            print("ℹ️  No current CSV file to backup")
            return False
        
        # Move file to backup directory
        backup_path = self.backup_dir / current_csv.name
        shutil.move(str(current_csv), str(backup_path))
        print(f"✅ Backed up: {current_csv.name} → backups/")
        
        return True
    
    def save_new_csv(self, source_path: Path, timestamp: Optional[datetime] = None) -> Path:
        """
        Save new CSV file to data directory with timestamp
        
        Args:
            source_path: Path to source CSV file
            timestamp: Optional timestamp (uses current time if not provided)
        
        Returns:
            Path to the saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Generate timestamped filename
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        new_filename = f"信用卡資料模板_{timestamp_str}.csv"
        destination = self.data_dir / new_filename
        
        # Copy file to data directory
        shutil.copy2(str(source_path), str(destination))
        print(f"✅ Saved new CSV: {new_filename}")
        
        return destination
    
    def cleanup_old_backups(self):
        """
        Clean up old backup files, keeping only the most recent max_backups
        """
        backup_files = sorted(self.backup_dir.glob(self.file_pattern))
        
        if len(backup_files) <= self.max_backups:
            print(f"ℹ️  Backups: {len(backup_files)}/{self.max_backups} (no cleanup needed)")
            return
        
        # Delete oldest backups
        files_to_delete = backup_files[:-self.max_backups]
        
        for file_path in files_to_delete:
            file_path.unlink()
            print(f"🗑️  Deleted old backup: {file_path.name}")
        
        print(f"✅ Cleaned up {len(files_to_delete)} old backups, kept {self.max_backups} most recent")
    
    def migrate_legacy_csv(self, legacy_path: Path) -> Optional[Path]:
        """
        Migrate legacy CSV file (without timestamp) to new naming scheme
        
        Args:
            legacy_path: Path to legacy CSV file
        
        Returns:
            Path to migrated file, or None if migration failed
        """
        if not legacy_path.exists():
            return None
        
        print(f"🔄 Migrating legacy CSV: {legacy_path.name}")
        
        # Use file modification time as timestamp
        mtime = datetime.fromtimestamp(legacy_path.stat().st_mtime)
        
        # Save with timestamp
        new_path = self.save_new_csv(legacy_path, timestamp=mtime)
        
        # Delete original
        legacy_path.unlink()
        print(f"✅ Migrated: {legacy_path.name} → {new_path.name}")
        
        return new_path
    
    def get_backup_count(self) -> int:
        """Get the number of backup files"""
        return len(list(self.backup_dir.glob(self.file_pattern)))
    
    def list_backups(self) -> List[Path]:
        """
        List all backup files, sorted by timestamp (newest first)
        
        Returns:
            List of backup file paths
        """
        return sorted(self.backup_dir.glob(self.file_pattern), reverse=True)
