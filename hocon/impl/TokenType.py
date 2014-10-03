from enum import Enum


TokenType = Enum('TokenType', (
    'start',
    'end',
    'comma',
    'equals',
    'colon',
    'open_curly',
    'close_curly',
    'open_square',
    'close_square',
    'value',
    'newline',
    'unquoted_text',
    'substitution',
    'problem',
    'comment',
    'plus_equals',
))
