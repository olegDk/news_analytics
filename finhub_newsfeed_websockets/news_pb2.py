# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: news.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='news.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\nnews.proto\",\n\x08Security\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x10\n\x08\x65xchange\x18\x02 \x01(\t\"E\n\x07\x43ontent\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04\x62ody\x18\x02 \x01(\t\x12\x1d\n\nsecurities\x18\x03 \x03(\x0b\x32\t.Security\"E\n\x04News\x12\x19\n\x07\x63ontent\x18\x01 \x01(\x0b\x32\x08.Content\x12\x11\n\ttimestamp\x18\x02 \x01(\t\x12\x0f\n\x07sources\x18\x03 \x03(\tb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SECURITY = _descriptor.Descriptor(
  name='Security',
  full_name='Security',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='symbol', full_name='Security.symbol', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exchange', full_name='Security.exchange', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=14,
  serialized_end=58,
)


_CONTENT = _descriptor.Descriptor(
  name='Content',
  full_name='Content',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='title', full_name='Content.title', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='body', full_name='Content.body', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='securities', full_name='Content.securities', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=60,
  serialized_end=129,
)


_NEWS = _descriptor.Descriptor(
  name='News',
  full_name='News',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='content', full_name='News.content', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='News.timestamp', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sources', full_name='News.sources', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=131,
  serialized_end=200,
)

_CONTENT.fields_by_name['securities'].message_type = _SECURITY
_NEWS.fields_by_name['content'].message_type = _CONTENT
DESCRIPTOR.message_types_by_name['Security'] = _SECURITY
DESCRIPTOR.message_types_by_name['Content'] = _CONTENT
DESCRIPTOR.message_types_by_name['News'] = _NEWS

Security = _reflection.GeneratedProtocolMessageType('Security', (_message.Message,), dict(
  DESCRIPTOR = _SECURITY,
  __module__ = 'news_pb2'
  # @@protoc_insertion_point(class_scope:Security)
  ))
_sym_db.RegisterMessage(Security)

Content = _reflection.GeneratedProtocolMessageType('Content', (_message.Message,), dict(
  DESCRIPTOR = _CONTENT,
  __module__ = 'news_pb2'
  # @@protoc_insertion_point(class_scope:Content)
  ))
_sym_db.RegisterMessage(Content)

News = _reflection.GeneratedProtocolMessageType('News', (_message.Message,), dict(
  DESCRIPTOR = _NEWS,
  __module__ = 'news_pb2'
  # @@protoc_insertion_point(class_scope:News)
  ))
_sym_db.RegisterMessage(News)


# @@protoc_insertion_point(module_scope)
