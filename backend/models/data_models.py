from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'http://example.org/my_schema/',
     'id': 'http://example.org/my_schema',
     'imports': ['linkml:types'],
     'name': 'my_schema',
     'source_file': 'test.yaml'} )


class Project(ConfiguredBaseModel):
    """
    A project entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    id: str = Field(default=..., description="""Unique UUIDv4 identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project', 'User', 'Issue', 'IssueCreate', 'Edge']} })
    class_name: Literal["Project"] = Field(default="Project", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    name: Optional[str] = Field(default=None, description="""Name""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project', 'ProjectCreate', 'User', 'UserCreate']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class ProjectCreate(ConfiguredBaseModel):
    """
    A project entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    class_name: Literal["ProjectCreate"] = Field(default="ProjectCreate", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    name: Optional[str] = Field(default=None, description="""Name""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project', 'ProjectCreate', 'User', 'UserCreate']} })


class User(ConfiguredBaseModel):
    """
    A user entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    id: str = Field(default=..., description="""Unique UUIDv4 identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project', 'User', 'Issue', 'IssueCreate', 'Edge']} })
    class_name: Literal["User"] = Field(default="User", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    name: Optional[str] = Field(default=None, description="""Name""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project', 'ProjectCreate', 'User', 'UserCreate']} })
    email: Optional[str] = Field(default=None, description="""Email address""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['User', 'UserCreate']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('email')
    def pattern_email(cls, v):
        pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid email format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid email format: {v}"
            raise ValueError(err_msg)
        return v


class UserCreate(ConfiguredBaseModel):
    """
    A user entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    class_name: Literal["UserCreate"] = Field(default="UserCreate", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    name: Optional[str] = Field(default=None, description="""Name""", json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project', 'ProjectCreate', 'User', 'UserCreate']} })
    email: Optional[str] = Field(default=None, description="""Email address""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['User', 'UserCreate']} })

    @field_validator('email')
    def pattern_email(cls, v):
        pattern=re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid email format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid email format: {v}"
            raise ValueError(err_msg)
        return v


class Issue(ConfiguredBaseModel):
    """
    An issue or ticket entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    id: str = Field(default=..., description="""Unique UUIDv4 identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project', 'User', 'Issue', 'IssueCreate', 'Edge']} })
    class_name: Literal["Issue"] = Field(default="Issue", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    title: Optional[str] = Field(default=None, description="""Title""", json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['Issue', 'IssueCreate']} })
    description: Optional[str] = Field(default=None, description="""Description""", json_schema_extra = { "linkml_meta": {'alias': 'description', 'domain_of': ['Issue', 'IssueCreate']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class IssueCreate(ConfiguredBaseModel):
    """
    An issue or ticket entity in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    id: str = Field(default=..., description="""Unique UUIDv4 identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project', 'User', 'Issue', 'IssueCreate', 'Edge']} })
    class_name: Literal["IssueCreate"] = Field(default="IssueCreate", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    title: Optional[str] = Field(default=None, description="""Title""", json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['Issue', 'IssueCreate']} })
    description: Optional[str] = Field(default=None, description="""Description""", json_schema_extra = { "linkml_meta": {'alias': 'description', 'domain_of': ['Issue', 'IssueCreate']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class Edge(ConfiguredBaseModel):
    """
    Represents a relationship (edge) between two entities in the graph.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'http://example.org/my_schema'})

    id: str = Field(default=..., description="""Unique UUIDv4 identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project', 'User', 'Issue', 'IssueCreate', 'Edge']} })
    class_name: Literal["Edge"] = Field(default="Edge", description="""The class name of the entity (automatically populated during serialization)""", json_schema_extra = { "linkml_meta": {'alias': 'class_name',
         'designates_type': True,
         'domain_of': ['Project',
                       'ProjectCreate',
                       'User',
                       'UserCreate',
                       'Issue',
                       'IssueCreate',
                       'Edge']} })
    source: Optional[str] = Field(default=None, description="""The source entity id (UUIDv4) of the relationship""", json_schema_extra = { "linkml_meta": {'alias': 'source', 'domain_of': ['Edge']} })
    target: Optional[str] = Field(default=None, description="""The target entity id (UUIDv4) of the relationship""", json_schema_extra = { "linkml_meta": {'alias': 'target', 'domain_of': ['Edge']} })
    label: Optional[str] = Field(default=None, description="""The type or label of the relationship""", json_schema_extra = { "linkml_meta": {'alias': 'label', 'domain_of': ['Edge']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('source')
    def pattern_source(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid source format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid source format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('target')
    def pattern_target(cls, v):
        pattern=re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid target format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid target format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Project.model_rebuild()
ProjectCreate.model_rebuild()
User.model_rebuild()
UserCreate.model_rebuild()
Issue.model_rebuild()
IssueCreate.model_rebuild()
Edge.model_rebuild()

