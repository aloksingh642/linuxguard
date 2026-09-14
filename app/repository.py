from sqlalchemy.orm import Session

from app.models import Scan, CleanupAction


def save_scan(engine, usage):

    with Session(engine) as session:

        scan = Scan(
            total_size=usage["total"],
            used_size=usage["used"],
            free_size=usage["free"],
            usage_percent=usage["percent"]
        )

        session.add(scan)
        session.commit()

        scan_id = scan.id
        usage_percent = scan.usage_percent
         
        return scan_id, usage_percent


def get_all_scans(engine):

    with Session(engine) as session:

        return session.query(Scan).all()
def save_cleanup_action(engine, file_path, action, status):

    with Session(engine) as session:

        cleanup = CleanupAction(
            file_path=str(file_path),
            action=action,
            status=status
        )

        session.add(cleanup)
        session.commit()

        return cleanup.id
