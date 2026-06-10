"""hr admin modules: departments, recruiting, hr documents

Revision ID: 006
Revises: 005
Create Date: 2026-06-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("competencies", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(op.f("ix_departments_code"), "departments", ["code"], unique=True)

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("source", sa.String(length=50), server_default="manual", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="new", nullable=False),
        sa.Column("consent_given", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("confirmed_department_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_department_id"], ["departments.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_candidates_id"), "candidates", ["id"], unique=False)

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resumes_id"), "resumes", ["id"], unique=False)
    op.create_index(
        op.f("ix_resumes_candidate_id"), "resumes", ["candidate_id"], unique=False
    )

    op.create_table(
        "resume_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("parsed_json", sa.JSON(), nullable=True),
        sa.Column("llm_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resume_analyses_id"), "resume_analyses", ["id"], unique=False)
    op.create_index(
        op.f("ix_resume_analyses_resume_id"),
        "resume_analyses",
        ["resume_id"],
        unique=False,
    )

    op.create_table(
        "department_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("rank", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(
            ["analysis_id"], ["resume_analyses.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_department_matches_id"), "department_matches", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_department_matches_analysis_id"),
        "department_matches",
        ["analysis_id"],
        unique=False,
    )

    op.create_table(
        "recruiting_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=True),
        sa.Column("min_score", sa.Integer(), server_default="40", nullable=False),
        sa.Column("top_n", sa.Integer(), server_default="3", nullable=False),
        sa.Column("llm_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "hr_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("doc_type", sa.String(length=128), server_default="other", nullable=False),
        sa.Column("owner_employee_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="draft", nullable=False),
        sa.Column("current_version_no", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_employee_id"], ["employees.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hr_documents_id"), "hr_documents", ["id"], unique=False)
    op.create_index(
        op.f("ix_hr_documents_owner_employee_id"),
        "hr_documents",
        ["owner_employee_id"],
        unique=False,
    )

    op.create_table(
        "hr_document_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("uploaded_by", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["hr_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hr_document_versions_id"), "hr_document_versions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_hr_document_versions_document_id"),
        "hr_document_versions",
        ["document_id"],
        unique=False,
    )

    op.create_table(
        "hr_document_workflows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hr_document_workflows_id"), "hr_document_workflows", ["id"], unique=False
    )

    op.create_table(
        "hr_document_workflow_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), server_default="hr", nullable=False),
        sa.Column("approver_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["workflow_id"], ["hr_document_workflows.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hr_document_workflow_steps_id"),
        "hr_document_workflow_steps",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_hr_document_workflow_steps_workflow_id"),
        "hr_document_workflow_steps",
        ["workflow_id"],
        unique=False,
    )

    op.create_table(
        "hr_document_instances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("current_step_order", sa.Integer(), server_default="1", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["hr_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["workflow_id"], ["hr_document_workflows.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hr_document_instances_id"), "hr_document_instances", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_hr_document_instances_document_id"),
        "hr_document_instances",
        ["document_id"],
        unique=False,
    )

    op.create_table(
        "hr_document_approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("instance_id", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["instance_id"], ["hr_document_instances.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_hr_document_approvals_id"), "hr_document_approvals", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_hr_document_approvals_instance_id"),
        "hr_document_approvals",
        ["instance_id"],
        unique=False,
    )

    op.add_column("employees", sa.Column("department_id", sa.Integer(), nullable=True))
    op.add_column("employees", sa.Column("candidate_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_employees_department_id",
        "employees",
        "departments",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_employees_candidate_id",
        "employees",
        "candidates",
        ["candidate_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_employees_candidate_id", "employees", type_="foreignkey")
    op.drop_constraint("fk_employees_department_id", "employees", type_="foreignkey")
    op.drop_column("employees", "candidate_id")
    op.drop_column("employees", "department_id")

    op.drop_table("hr_document_approvals")
    op.drop_table("hr_document_instances")
    op.drop_table("hr_document_workflow_steps")
    op.drop_table("hr_document_workflows")
    op.drop_table("hr_document_versions")
    op.drop_table("hr_documents")
    op.drop_table("recruiting_settings")
    op.drop_table("department_matches")
    op.drop_table("resume_analyses")
    op.drop_table("resumes")
    op.drop_table("candidates")
    op.drop_table("departments")
