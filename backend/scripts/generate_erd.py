import os
import sys
from sqlalchemy_schemadisplay import create_schema_graph

# 👇 Add backend/ to Python path so "app" can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import engine
from app.db import models  # noqa

if __name__ == "__main__":
    print("🧠 Generating ERD diagram...")

    graph = create_schema_graph(
        engine=engine,  # ✅ added
        metadata=Base.metadata,
        show_datatypes=True,
        show_indexes=False,
        rankdir='LR',
        concentrate=False
    )

    output_path = os.path.join(os.path.dirname(__file__), "..", "erd.png")
    graph.write_png(output_path)
    print(f"✅ ERD diagram generated at: {output_path}")
