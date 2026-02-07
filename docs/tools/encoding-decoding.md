# Encoding, Decoding & Conversion Tools

> Base64, binary, Morse code, string escaping, number base conversion, JSON/XML processing, hash generation, and timestamp conversion.

---

## Encoding/Decoding Tools Documentation

### Base64 Encoder/Decoder

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**TextProcessor Method**: `base64_processor()`

#### Description

The Base64 Encoder/Decoder is a bidirectional encoding tool that converts text to and from Base64 format. Base64 encoding is commonly used for encoding binary data in text format, making it safe for transmission over text-based protocols and storage in text-based systems.

#### Key Features

- **Bidirectional Processing**: Both encoding and decoding capabilities
- **UTF-8 Support**: Handles Unicode text with proper UTF-8 encoding
- **Error Handling**: Comprehensive error handling for invalid input
- **ASCII Output**: Produces clean ASCII output for encoded data
- **Standard Compliance**: Uses Python's standard base64 library

#### Capabilities

##### Core Functionality
- **Encoding**: Converts plain text to Base64 encoded format
- **Decoding**: Converts Base64 encoded text back to plain text
- **UTF-8 Processing**: Properly handles international characters and symbols
- **Error Recovery**: Graceful handling of malformed Base64 input

##### Encoding Process
1. **Text Input**: Accepts any UTF-8 text input
2. **UTF-8 Encoding**: Converts text to UTF-8 bytes
3. **Base64 Encoding**: Encodes bytes to Base64 format
4. **ASCII Output**: Returns ASCII-safe Base64 string

##### Decoding Process
1. **Base64 Input**: Accepts Base64 encoded string
2. **Base64 Decoding**: Decodes Base64 to bytes
3. **UTF-8 Decoding**: Converts bytes back to UTF-8 text
4. **Text Output**: Returns original plain text

##### Input/Output Specifications
- **Encoding Input**: Any UTF-8 text (including special characters, emojis, etc.)
- **Encoding Output**: Base64 encoded ASCII string
- **Decoding Input**: Valid Base64 encoded string
- **Decoding Output**: Original UTF-8 text
- **Performance**: Fast processing for typical text sizes

#### Configuration

##### Settings Panel Options
- **Encode**: Convert plain text to Base64 format
- **Decode**: Convert Base64 encoded text back to plain text

##### Default Settings
```json
{
  "mode": "encode"
}
```

#### Usage Examples

##### Basic Text Encoding Example
**Input:**
```
Hello, World!
```

**Configuration:**
- Mode: Encode

**Output:**
```
SGVsbG8sIFdvcmxkIQ==
```

##### Basic Text Decoding Example
**Input:**
```
SGVsbG8sIFdvcmxkIQ==
```

**Configuration:**
- Mode: Decode

**Output:**
```
Hello, World!
```

##### Unicode Text Encoding Example
**Input:**
```
Hello 世界! 🌍 Café
```

**Configuration:**
- Mode: Encode

**Output:**
```
SGVsbG8g5LiW55WMISAg8J+MjSBDYWbDqQ==
```

##### Unicode Text Decoding Example
**Input:**
```
SGVsbG8g5LiW55WMISAg8J+MjSBDYWbDqQ==
```

**Configuration:**
- Mode: Decode

**Output:**
```
Hello 世界! 🌍 Café
```

##### Multi-line Text Encoding Example
**Input:**
```
Line 1: First line
Line 2: Second line
Line 3: Third line
```

**Configuration:**
- Mode: Encode

**Output:**
```
TGluZSAxOiBGaXJzdCBsaW5lCkxpbmUgMjogU2Vjb25kIGxpbmUKTGluZSAzOiBUaGlyZCBsaW5l
```

##### Special Characters Encoding Example
**Input:**
```
Special chars: !@#$%^&*()_+-=[]{}|;:'"<>?,.
```

**Configuration:**
- Mode: Encode

**Output:**
```
U3BlY2lhbCBjaGFyczogIUAjJCVeJiooKV8rLT1bXXt9fDs6JyI8Pj8sLg==
```

#### Common Use Cases

1. **Data Transmission**: Encode binary data for safe transmission over text protocols
2. **Email Attachments**: Encode files for email transmission (MIME encoding)
3. **Web Development**: Encode data for URLs or web storage
4. **Configuration Files**: Store binary data in text-based configuration files
5. **API Communication**: Encode binary payloads for REST API calls
6. **Database Storage**: Store binary data in text fields
7. **Obfuscation**: Simple obfuscation of text data (not for security)
8. **Data Interchange**: Exchange binary data between different systems

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def base64_processor(text, mode):
    """Encodes or decodes text using Base64."""
    try:
        if mode == "encode":
            return base64.b64encode(text.encode('utf-8')).decode('ascii')
        else: # mode == "decode"
            return base64.b64decode(text.encode('ascii')).decode('utf-8')
    except Exception as e:
        return f"Base64 Error: {e}"
```

##### Algorithm Details
**Encoding Process:**
1. Convert input text to UTF-8 bytes using `text.encode('utf-8')`
2. Apply Base64 encoding using `base64.b64encode()`
3. Convert result to ASCII string using `.decode('ascii')`

**Decoding Process:**
1. Convert Base64 string to ASCII bytes using `text.encode('ascii')`
2. Apply Base64 decoding using `base64.b64decode()`
3. Convert result to UTF-8 text using `.decode('utf-8')`

##### Dependencies
- **Required**: Python standard library (base64 module)
- **Optional**: None

##### Performance Considerations
- **Memory Efficient**: Processes text in memory without temporary files
- **Fast Processing**: Uses optimized standard library implementation
- **Size Overhead**: Base64 encoding increases size by approximately 33%

#### Error Handling

##### Invalid Base64 Input (Decoding)
**Input:**
```
This is not valid Base64!
```

**Configuration:**
- Mode: Decode

**Output:**
```
Base64 Error: Invalid base64-encoded string: number of data characters (25) cannot be 1 more than a multiple of 4
```

##### Empty Input
**Input:**
```
(empty)
```

**Configuration:**
- Mode: Encode or Decode

**Output:**
```
(empty string)
```

##### Malformed Base64 Characters
**Input:**
```
SGVsbG8@#$%^&*()
```

**Configuration:**
- Mode: Decode

**Output:**
```
Base64 Error: Non-base64 digit found
```

#### Base64 Format Details

##### Character Set
Base64 uses 64 characters for encoding:
- **A-Z**: Uppercase letters (26 characters)
- **a-z**: Lowercase letters (26 characters)  
- **0-9**: Digits (10 characters)
- **+**: Plus sign (1 character)
- **/**: Forward slash (1 character)
- **=**: Padding character (used for alignment)

##### Padding
- Base64 uses `=` characters for padding to ensure output length is multiple of 4
- One `=`: Input length was 1 more than multiple of 3
- Two `==`: Input length was 2 more than multiple of 3

##### Size Calculation
- **Encoding**: Output size ≈ (input_bytes × 4) ÷ 3, rounded up to multiple of 4
- **Decoding**: Output size ≈ (input_length × 3) ÷ 4

#### Best Practices

##### Recommended Usage
- **Data Integrity**: Verify decoded data matches original when possible
- **Error Handling**: Always check for encoding/decoding errors
- **Size Awareness**: Remember Base64 increases data size by ~33%
- **Character Safety**: Use Base64 for binary data in text contexts

##### Performance Tips
- **Large Data**: For very large data, consider streaming approaches
- **Memory Usage**: Tool processes entire input in memory
- **Validation**: Validate Base64 format before attempting to decode
- **Encoding Choice**: Consider alternatives for very large binary data

##### Common Pitfalls
- **Not for Security**: Base64 is encoding, not encryption (easily reversible)
- **Size Increase**: Encoded data is larger than original
- **Character Corruption**: Ensure Base64 strings aren't modified during transmission
- **Line Breaks**: Some Base64 implementations add line breaks (this tool doesn't)

#### Security Considerations

##### Important Notes
- **Not Encryption**: Base64 is easily reversible and provides no security
- **Obfuscation Only**: Provides minimal obfuscation, not protection
- **Data Exposure**: Encoded data can be easily decoded by anyone
- **Sensitive Data**: Don't rely on Base64 for protecting sensitive information

##### Appropriate Uses
- **Data Transmission**: Safe for transmitting binary data over text protocols
- **Storage Format**: Suitable for storing binary data in text fields
- **Compatibility**: Good for ensuring data compatibility across systems
- **Encoding Standard**: Widely supported standard for data encoding

#### Integration with Other Tools

##### Workflow Examples
1. **Encode → Store → Decode**:
   - Base64 Encoder → (store/transmit) → Base64 Decoder

2. **Process → Encode → Transmit**:
   - Text processing → Base64 Encoder → (API/email transmission)

3. **Decode → Process → Re-encode**:
   - Base64 Decoder → Find & Replace → Base64 Encoder

#### Related Tools

- **Binary Code Translator**: Convert text to binary representation
- **Morse Code Translator**: Convert text to Morse code format
- **URL Parser**: Parse URLs that may contain Base64 encoded data
- **Find & Replace Text**: Process text before or after encoding

#### See Also
- [Binary Code Translator Documentation](#binary-code-translator)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Data Transmission Best Practices](#common-use-cases)###
 Binary Code Translator

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**TextProcessor Method**: `binary_translator()`

#### Description

The Binary Code Translator is an intelligent bidirectional converter that translates text to binary code and binary code back to text. It features automatic input detection, converting text to 8-bit binary representation or binary sequences back to readable text, making it useful for educational purposes, data analysis, and binary data processing.

#### Key Features

- **Automatic Detection**: Intelligently detects whether input is text or binary
- **Bidirectional Conversion**: Converts text to binary and binary to text
- **8-bit Representation**: Uses standard 8-bit binary format for characters
- **Space Separation**: Binary output is space-separated for readability
- **Error Handling**: Robust error handling for invalid binary sequences
- **Unicode Support**: Handles all Unicode characters through ASCII/UTF-8 encoding

#### Capabilities

##### Core Functionality
- **Text to Binary**: Converts each character to its 8-bit binary representation
- **Binary to Text**: Converts space-separated binary sequences back to text
- **Automatic Mode Detection**: Determines conversion direction based on input content
- **Character Encoding**: Uses ASCII/Unicode character codes for conversion

##### Input Detection Logic
- **Binary Input**: Detected when input contains only spaces, 0s, and 1s
- **Text Input**: Any input containing characters other than spaces, 0s, and 1s
- **Automatic Processing**: No manual mode selection required

##### Binary Format
- **8-bit Format**: Each character represented as 8-bit binary (e.g., 01000001 for 'A')
- **Space Separation**: Binary codes separated by spaces for readability
- **Leading Zeros**: Maintains leading zeros for consistent 8-bit format

##### Input/Output Specifications
- **Text Input**: Any text characters (ASCII, Unicode)
- **Binary Input**: Space-separated 8-bit binary sequences (e.g., "01001000 01100101")
- **Text Output**: Readable text characters
- **Binary Output**: Space-separated 8-bit binary codes
- **Performance**: Fast conversion for typical text sizes

#### Configuration

The Binary Code Translator operates without configuration options - it automatically detects input type and performs the appropriate conversion.

#### Usage Examples

##### Basic Text to Binary Example
**Input:**
```
Hello
```

**Output:**
```
01001000 01100101 01101100 01101100 01101111
```

##### Basic Binary to Text Example
**Input:**
```
01001000 01100101 01101100 01101100 01101111
```

**Output:**
```
Hello
```

##### Numbers and Symbols Example
**Input:**
```
123!@#
```

**Output:**
```
00110001 00110010 00110011 00100001 01000000 00100011
```

##### Special Characters Example
**Input:**
```
Hello, World!
```

**Output:**
```
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

##### Binary to Text Conversion Example
**Input:**
```
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

**Output:**
```
Hello, World!
```

##### Mixed Case Text Example
**Input:**
```
AbC
```

**Output:**
```
01000001 01100010 01000011
```

##### Punctuation and Spaces Example
**Input:**
```
A B.
```

**Output:**
```
01000001 00100000 01000010 00101110
```

##### Single Character Examples
**Input:** `A`
**Output:** `01000001`

**Input:** `01000001`
**Output:** `A`

#### Common Use Cases

1. **Educational Purposes**: Teaching binary representation and computer fundamentals
2. **Data Analysis**: Analyzing binary patterns in text data
3. **Debugging**: Converting text to binary for low-level debugging
4. **Cryptography Learning**: Understanding binary representation in encryption
5. **Programming Education**: Demonstrating character encoding concepts
6. **Data Conversion**: Converting between text and binary formats
7. **System Administration**: Analyzing binary data in logs or files
8. **Digital Forensics**: Examining binary representations of text data

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def binary_translator(text):
    """Translates text to or from binary."""
    # Detect if input is binary or text
    if all(c in ' 01' for c in text): # Binary to Text
        try:
            return ''.join(chr(int(b, 2)) for b in text.split())
        except (ValueError, TypeError):
            return "Error: Invalid binary sequence."
    else: # Text to Binary
        return ' '.join(format(ord(char), '08b') for char in text)
```

##### Algorithm Details

**Input Detection:**
- Uses `all(c in ' 01' for c in text)` to detect binary input
- Binary input must contain only spaces, zeros, and ones

**Text to Binary Conversion:**
1. Iterate through each character in the input text
2. Get ASCII/Unicode code using `ord(char)`
3. Convert to 8-bit binary using `format(code, '08b')`
4. Join all binary codes with spaces

**Binary to Text Conversion:**
1. Split input by spaces to get individual binary codes
2. Convert each binary string to integer using `int(b, 2)`
3. Convert integer to character using `chr()`
4. Join all characters to form final text

##### Character Encoding
- **ASCII Characters**: Standard ASCII characters (0-127)
- **Extended ASCII**: Extended ASCII characters (128-255)
- **Unicode**: Basic Unicode characters supported through ord()/chr()

##### Dependencies
- **Required**: Python standard library (built-in functions)
- **Optional**: None

##### Performance Considerations
- **Memory Efficient**: Processes characters individually without large buffers
- **Fast Conversion**: Uses efficient built-in Python functions
- **Size Expansion**: Binary output is approximately 9x larger than input (8 bits + space per character)

#### Error Handling

##### Invalid Binary Sequence
**Input:**
```
01001000 01100101 11111111
```

**Output:**
```
Error: Invalid binary sequence.
```

##### Malformed Binary Input
**Input:**
```
01001000 0110010 01101100
```
(Note: Second sequence has only 7 bits)

**Output:**
```
Error: Invalid binary sequence.
```

##### Non-Binary Characters in Binary Mode
**Input:**
```
01001000 01100101 xyz
```

**Output:**
```
Error: Invalid binary sequence.
```

##### Empty Input
**Input:**
```
(empty)
```

**Output:**
```
(empty string)
```

#### Binary Code Reference

##### Common Characters
| Character | ASCII Code | Binary Code |
|-----------|------------|-------------|
| A | 65 | 01000001 |
| B | 66 | 01000010 |
| a | 97 | 01100001 |
| b | 98 | 01100010 |
| 0 | 48 | 00110000 |
| 1 | 49 | 00110001 |
| Space | 32 | 00100000 |
| ! | 33 | 00100001 |
| . | 46 | 00101110 |
| , | 44 | 00101100 |

##### Special Characters
| Character | ASCII Code | Binary Code |
|-----------|------------|-------------|
| @ | 64 | 01000000 |
| # | 35 | 00100011 |
| $ | 36 | 00100100 |
| % | 37 | 00100101 |
| & | 38 | 00100110 |
| * | 42 | 00101010 |
| ( | 40 | 00101000 |
| ) | 41 | 00101001 |

#### Best Practices

##### Recommended Usage
- **Educational Context**: Excellent for teaching binary concepts
- **Data Analysis**: Useful for analyzing binary patterns
- **Verification**: Cross-check binary conversions with other tools
- **Format Consistency**: Maintain space separation in binary sequences

##### Performance Tips
- **Large Texts**: Tool handles typical text sizes efficiently
- **Memory Usage**: Binary output requires significantly more space
- **Validation**: Verify binary sequences before conversion
- **Character Limits**: Be aware of memory usage with very large texts

##### Common Pitfalls
- **Binary Format**: Binary input must be space-separated 8-bit sequences
- **Character Encoding**: Limited to characters supported by ord()/chr()
- **Size Expansion**: Binary representation is much larger than original text
- **Input Detection**: Mixed binary/text input may not be detected correctly

#### Educational Applications

##### Learning Binary Representation
1. **Character Codes**: Understand how characters are represented in binary
2. **ASCII Table**: Learn ASCII character codes and their binary equivalents
3. **Data Storage**: Understand how text is stored in computer memory
4. **Bit Patterns**: Recognize patterns in binary representations

##### Programming Concepts
1. **Character Encoding**: Understand ASCII and Unicode encoding
2. **Data Types**: Learn about character and string data types
3. **Number Systems**: Practice converting between decimal and binary
4. **Bitwise Operations**: Foundation for understanding bitwise operations

#### Integration with Other Tools

##### Workflow Examples
1. **Convert → Analyze → Convert Back**:
   - Text → Binary Code Translator → (analysis) → Binary Code Translator → Text

2. **Process → Convert → Store**:
   - Find & Replace → Binary Code Translator → (storage/transmission)

3. **Convert → Compare → Analyze**:
   - Binary Code Translator → Diff Viewer → Word Frequency Counter

#### Related Tools

- **Base64 Encoder/Decoder**: Alternative encoding method for text data
- **Morse Code Translator**: Another encoding system for text
- **Word Frequency Counter**: Analyze patterns in binary output
- **Find & Replace Text**: Process text before or after binary conversion

#### See Also
- [Base64 Encoder/Decoder Documentation](#base64-encoderdecoder)
- [Morse Code Translator Documentation](#morse-code-translator)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Educational Applications](#educational-applications)###
 Morse Code Translator

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available (Audio features conditional on PyAudio)  
**TextProcessor Method**: `morse_translator()`

#### Description

The Morse Code Translator is a comprehensive bidirectional converter that translates text to Morse code and Morse code back to text. It features a complete International Morse Code dictionary, audio playback capabilities, and support for letters, numbers, and common punctuation marks, making it perfect for educational purposes, amateur radio, and historical communication methods.

#### Key Features

- **Bidirectional Translation**: Convert text to Morse code and Morse code to text
- **Complete Character Set**: Supports all letters, numbers, and common punctuation
- **Audio Playback**: Play Morse code audio with configurable tone frequency (requires PyAudio)
- **International Standard**: Uses standard International Morse Code
- **Space Handling**: Proper handling of spaces and word separation
- **Case Insensitive**: Automatically converts text to uppercase for processing

#### Capabilities

##### Core Functionality
- **Text to Morse**: Converts text characters to Morse code dots and dashes
- **Morse to Text**: Converts Morse code back to readable text
- **Audio Generation**: Generates audio tones for Morse code playback
- **Character Support**: Full alphabet, numbers 0-9, and punctuation marks

##### Supported Characters

**Letters (A-Z):**
- A: `.-`    B: `-...`  C: `-.-.`  D: `-..`   E: `.`
- F: `..-.`  G: `--.`   H: `....`  I: `..`    J: `.---`
- K: `-.-`   L: `.-..`  M: `--`    N: `-.`    O: `---`
- P: `.--.`  Q: `--.-`  R: `.-.`   S: `...`   T: `-`
- U: `..-`   V: `...-`  W: `.--`   X: `-..-`  Y: `-.--`
- Z: `--..`

**Numbers (0-9):**
- 0: `-----`  1: `.----`  2: `..---`  3: `...--`  4: `....-`
- 5: `.....`  6: `-....`  7: `--...`  8: `---..`  9: `----.`

**Punctuation:**
- Space: `/` (word separator)
- Comma: `--..--`
- Period: `.-.-.-`
- Question Mark: `..--..`
- Slash: `-..-.`
- Hyphen: `-....-`
- Left Parenthesis: `-.--.-`
- Right Parenthesis: `-.--.-`

##### Audio Features (Optional)
- **Tone Generation**: Configurable tone frequency (default: 700 Hz)
- **Timing Standards**: Standard Morse code timing for dots, dashes, and spaces
- **Playback Control**: Start and stop audio playback
- **Threading**: Non-blocking audio playback in separate thread

##### Input/Output Specifications
- **Text Input**: Any text containing supported characters
- **Morse Input**: Space-separated Morse code sequences
- **Text Output**: Uppercase text characters
- **Morse Output**: Space-separated dots and dashes with `/` for word breaks
- **Performance**: Fast conversion for typical text sizes

#### Configuration

##### Settings Panel Options
- **Text to Morse**: Convert plain text to Morse code
- **Morse to Text**: Convert Morse code back to plain text
- **Play Morse Audio**: Play audio representation of Morse code (if PyAudio available)

##### Default Settings
```json
{
  "mode": "morse",
  "tone": 700
}
```

##### Audio Configuration
- **Tone Frequency**: Configurable in settings (default: 700 Hz)
- **Sample Rate**: 44,100 Hz
- **Dot Duration**: 80 milliseconds
- **Dash Duration**: 240 milliseconds (3x dot duration)

#### Usage Examples

##### Basic Text to Morse Example
**Input:**
```
HELLO
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. ---
```

##### Basic Morse to Text Example
**Input:**
```
.... . .-.. .-.. ---
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
HELLO
```

##### Text with Spaces Example
**Input:**
```
HELLO WORLD
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

##### Numbers and Punctuation Example
**Input:**
```
SOS 123
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
... --- ... / .---- ..--- ...--
```

##### Mixed Case Text Example
**Input:**
```
Hello World!
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -.. -.-.--
```
(Note: Exclamation mark not in standard dictionary, so it's omitted)

##### Complex Morse to Text Example
**Input:**
```
-- --- .-. ... . / -.-. --- -.. .
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
MORSE CODE
```

##### Punctuation Example
**Input:**
```
HELLO, WORLD.
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- --..-- / .-- --- .-. .-.. -.. .-.-.-
```

#### Common Use Cases

1. **Amateur Radio**: Communication using Morse code (CW)
2. **Educational Purposes**: Learning Morse code and telegraph history
3. **Emergency Communication**: Backup communication method
4. **Historical Recreation**: Recreating historical telegraph messages
5. **Accessibility**: Alternative communication method
6. **Puzzle Solving**: Decoding Morse code puzzles and games
7. **Military/Naval Training**: Learning traditional military communication
8. **Scout Activities**: Merit badge requirements and camping activities

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def morse_translator(text, mode, morse_dict, reversed_morse_dict):
    """Translates text to or from Morse code."""
    if mode == "morse":
        return ' '.join(morse_dict.get(char.upper(), '') for char in text)
    else: # mode == "text"
        return ''.join(reversed_morse_dict.get(code, '') for code in text.split(' '))
```

##### Algorithm Details

**Text to Morse Conversion:**
1. Convert input text to uppercase
2. For each character, look up Morse code in dictionary
3. Join Morse codes with spaces
4. Unknown characters are omitted (empty string)

**Morse to Text Conversion:**
1. Split input by spaces to get individual Morse codes
2. Look up each Morse code in reversed dictionary
3. Join characters to form final text
4. Unknown Morse codes are omitted

##### Morse Code Dictionary
The tool uses a comprehensive dictionary with 39 characters:
- 26 letters (A-Z)
- 10 numbers (0-9)
- 8 punctuation marks
- Space character (represented as `/`)

##### Audio Implementation (Optional)
```python
def generate_morse_tone(self, duration):
    """Generates a sine wave for a given duration for Morse code."""
    TONE_FREQ = self.settings["tool_settings"]["Morse Code Translator"].get("tone", 700)
    t = np.linspace(0, duration, int(44100 * duration), False)
    tone = np.sin(TONE_FREQ * t * 2 * np.pi)
    return tone
```

##### Dependencies
- **Required**: Python standard library
- **Optional**: PyAudio and NumPy for audio playback functionality

##### Performance Considerations
- **Fast Conversion**: Dictionary lookup is very efficient
- **Memory Usage**: Minimal memory usage for typical text sizes
- **Audio Processing**: Audio generation requires additional processing time

#### Audio Features

##### Morse Code Timing Standards
- **Dot**: 1 unit (80ms default)
- **Dash**: 3 units (240ms default)
- **Gap between dots/dashes**: 1 unit
- **Gap between letters**: 3 units
- **Gap between words**: 7 units

##### Audio Controls
- **Play Morse Audio**: Starts audio playback of Morse code in output area
- **Stop Playing**: Stops currently playing audio
- **Threading**: Audio plays in background without blocking UI

##### Audio Requirements
- **PyAudio**: Required for audio output
- **NumPy**: Required for tone generation
- **Sound Card**: System must have audio output capability

#### Best Practices

##### Recommended Usage
- **Standard Characters**: Use only supported characters for best results
- **Clear Spacing**: Ensure proper spacing in Morse code input
- **Audio Learning**: Use audio playback to learn Morse code timing
- **Practice**: Regular practice improves Morse code proficiency

##### Performance Tips
- **Large Texts**: Tool handles typical text sizes efficiently
- **Audio Playback**: Stop previous audio before starting new playback
- **Character Support**: Check character support before conversion
- **Timing Practice**: Use audio feature to learn proper timing

##### Common Pitfalls
- **Unsupported Characters**: Characters not in dictionary are omitted
- **Spacing Errors**: Incorrect spacing in Morse input affects conversion
- **Audio Dependencies**: Audio features require PyAudio installation
- **Case Sensitivity**: Tool converts to uppercase automatically

#### Morse Code Learning

##### Learning Tips
1. **Start with Letters**: Learn alphabet first, then numbers
2. **Use Audio**: Audio playback helps learn proper timing
3. **Practice Daily**: Regular practice improves speed and accuracy
4. **Common Words**: Start with common words and phrases
5. **Timing**: Focus on proper timing between elements

##### Memory Aids
- **Short Letters**: E(.), I(..), S(...), H(....)
- **Long Letters**: T(-), M(--), O(---), CH(....)
- **Numbers**: Follow logical patterns (1: .----, 2: ..---, etc.)

#### Error Handling

##### Unsupported Characters
Characters not in the Morse code dictionary are silently omitted from the output.

**Input:**
```
HELLO@WORLD
```

**Output:**
```
.... . .-.. .-.. --- .-- --- .-. .-.. -..
```
(@ symbol is omitted)

##### Invalid Morse Code
Invalid Morse code sequences are silently omitted from text conversion.

**Input:**
```
.... . .-.. xyz ---
```

**Output:**
```
HELO
```
(`xyz` is not valid Morse code and is omitted)

##### Audio Errors
If PyAudio is not available, audio features are disabled but text conversion still works.

#### Historical Context

##### Morse Code History
- **Invented**: 1830s by Samuel Morse
- **First Message**: "What hath God wrought" (1844)
- **International Standard**: Established in 1865
- **Amateur Radio**: Still widely used in ham radio
- **Emergency Use**: Recognized international distress signal (SOS)

##### Modern Applications
- **Amateur Radio**: CW (Continuous Wave) communication
- **Aviation**: Some navigation aids still use Morse code
- **Military**: Backup communication method
- **Education**: Teaching digital communication concepts

#### Integration with Other Tools

##### Workflow Examples
1. **Convert → Play → Learn**:
   - Text → Morse Code Translator → Audio Playback

2. **Decode → Verify → Process**:
   - Morse Code Translator → Case Tool → Find & Replace

3. **Practice → Compare → Improve**:
   - Morse Code Translator → Diff Viewer → (compare with reference)

#### Related Tools

- **Binary Code Translator**: Another encoding system for text
- **Base64 Encoder/Decoder**: Modern encoding method
- **Case Tool**: Format text before Morse conversion
- **Find & Replace Text**: Process Morse code patterns

#### See Also
- [Binary Code Translator Documentation](#binary-code-translator)
- [Base64 Encoder/Decoder Documentation](#base64-encoderdecoder)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Audio Features and Requirements](#audio-features)

---

### Translator Tools (NEW)

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available (Audio features require PyAudio)  
**Implementation**: `tools/translator_tools.py` - `TranslatorToolsWidget` class  
**TextProcessor Methods**: `morse_translator()`, `binary_translator()`

#### Description

Translator Tools is a comprehensive encoding/decoding utility that provides both Morse code and binary code translation capabilities through a tabbed interface. It offers bidirectional translation (text to code and code to text), with the Morse Code Translator featuring optional audio playback for learning and verification. The tool features a modern tabbed UI similar to Sorter Tools, with separate tabs for Morse Code Translator and Binary Code Translator.

#### Key Features

- **Tabbed Interface**: Separate tabs for Morse Code and Binary Code translation
- **Morse Code Translator**: Bidirectional Morse code translation with audio playback
- **Binary Code Translator**: Automatic detection of input type (text or binary)
- **Audio Playback** (Optional): Play Morse code with configurable tone frequency
- **International Support**: Full Unicode support for text translation
- **Error Handling**: Clear error messages for invalid binary sequences
- **Settings Persistence**: Translation mode settings saved across sessions
- **Real-time Processing**: Instant translation with visual feedback

#### Capabilities

##### Morse Code Translator Tab

**Core Functionality**:
- **Text to Morse**: Converts text to Morse code using dots (.) and dashes (-)
- **Morse to Text**: Converts Morse code back to readable text
- **Audio Playback**: Optional audio generation for Morse code (requires PyAudio)
- **Character Support**: Letters (A-Z), numbers (0-9), common punctuation
- **Word Separation**: Uses `/` for word boundaries, spaces for letter boundaries

**Morse Code Dictionary**:
- **Letters**: A-Z mapped to Morse patterns (e.g., A='.-', B='-...', etc.)
- **Numbers**: 0-9 mapped to Morse patterns (e.g., 1='.----', 2='..---', etc.)
- **Punctuation**: Common symbols (comma, period, question mark, slash, hyphen, parentheses)
- **Space**: Represented by `/` in Morse code
- **Total Characters**: 40+ characters supported

**Audio Features** (Optional - requires PyAudio):
- **Tone Frequency**: 700 Hz default tone
- **Dot Duration**: 80ms
- **Dash Duration**: 240ms (3× dot duration)
- **Letter Spacing**: 240ms between letters
- **Word Spacing**: 560ms between words (7× dot duration)
- **Playback Control**: Start/Stop button for audio playback
- **Threading**: Non-blocking audio playback in separate thread

##### Binary Code Translator Tab

**Core Functionality**:
- **Text to Binary**: Converts text to 8-bit binary representation
- **Binary to Text**: Converts binary code back to readable text
- **Auto-Detection**: Automatically detects if input is text or binary
- **Space Separation**: Binary bytes separated by spaces for readability
- **Error Handling**: Validates binary input and provides error messages

**Binary Format**:
- **8-bit Representation**: Each character encoded as 8-bit binary
- **Space Separated**: Binary bytes separated by spaces (e.g., "01001000 01101001")
- **UTF-8 Encoding**: Supports full UTF-8 character set
- **Bidirectional**: Automatically determines translation direction

**Auto-Detection Logic**:
- If input contains only `0`, `1`, and spaces → Binary to Text
- If input contains any other characters → Text to Binary
- Handles empty input gracefully

##### Input/Output Specifications

**Morse Code Translator**:
- **Text to Morse Input**: Any text with supported characters (A-Z, 0-9, punctuation)
- **Text to Morse Output**: Morse code with dots, dashes, spaces, and slashes
- **Morse to Text Input**: Morse code string with proper spacing
- **Morse to Text Output**: Original text (uppercase)
- **Performance**: Instant translation for typical text sizes

**Binary Code Translator**:
- **Text to Binary Input**: Any UTF-8 text
- **Text to Binary Output**: Space-separated 8-bit binary codes
- **Binary to Text Input**: Space-separated binary codes (8-bit)
- **Binary to Text Output**: Original UTF-8 text
- **Error Output**: "Error: Invalid binary sequence." for malformed input

#### Configuration

##### Tabbed Interface Layout

The Translator Tools widget uses a notebook/tabbed interface with two tabs:

**Tab 1: Morse Code Translator**
- **Translation Mode Frame** (Radio buttons):
  - Text to Morse: Convert text to Morse code
  - Morse to Text: Convert Morse code to text
- **Translate Button**: Applies Morse code translation
- **Play Morse Audio Button** (if PyAudio available): Plays Morse code audio

**Tab 2: Binary Code Translator**
- **Information Frame**: Explains auto-detection feature
  - Text → Binary (8-bit per character)
  - Binary → Text (space-separated binary)
- **Translate Button**: Applies binary translation (auto-detects direction)

##### Settings Persistence

Settings are stored in `settings.json` under `tool_settings`:

**Morse Code Translator Settings**:
```json
{
  "Morse Code Translator": {
    "mode": "morse",
    "tone": 700
  }
}
```

**Binary Code Translator Settings**:
```json
{
  "Binary Code Translator": {}
}
```

##### Default Settings

**Morse Code Translator**:
- Mode: morse (Text to Morse)
- Tone Frequency: 700 Hz

**Binary Code Translator**:
- No configurable settings (auto-detection)

#### Usage Examples

##### Example 1: Text to Morse Code
**Tab**: Morse Code Translator

**Input:**
```
HELLO WORLD
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

**Explanation**: Each letter converted to Morse code, spaces between letters, `/` between words.

##### Example 2: Morse Code to Text
**Tab**: Morse Code Translator

**Input:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
HELLO WORLD
```

**Explanation**: Morse code converted back to uppercase text.

##### Example 3: Morse Code with Numbers and Punctuation
**Tab**: Morse Code Translator

**Input:**
```
SOS 123
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
... --- ... / .---- ..--- ...--
```

**Explanation**: Letters and numbers both supported in Morse code.

##### Example 4: Text to Binary
**Tab**: Binary Code Translator

**Input:**
```
Hi
```

**Configuration:**
- Auto-detection (Text to Binary)

**Output:**
```
01001000 01101001
```

**Explanation**: Each character converted to 8-bit binary, space-separated.

##### Example 5: Binary to Text
**Tab**: Binary Code Translator

**Input:**
```
01001000 01101001
```

**Configuration:**
- Auto-detection (Binary to Text)

**Output:**
```
Hi
```

**Explanation**: Binary codes converted back to text characters.

##### Example 6: Binary with Special Characters
**Tab**: Binary Code Translator

**Input:**
```
Hello!
```

**Configuration:**
- Auto-detection (Text to Binary)

**Output:**
```
01001000 01100101 01101100 01101100 01101111 00100001
```

**Explanation**: All characters including punctuation converted to binary.

##### Example 7: Morse Code Audio Playback (if PyAudio available)
**Tab**: Morse Code Translator

**Input:**
```
SOS
```

**Configuration:**
- Mode: Text to Morse
- Click "Translate" first, then "Play Morse Audio"

**Output (Text):**
```
... --- ...
```

**Output (Audio)**: Plays Morse code audio with dots and dashes at 700 Hz

**Explanation**: Audio playback helps with learning Morse code patterns.

##### Example 8: Invalid Binary Input
**Tab**: Binary Code Translator

**Input:**
```
0101 1111 0000
```

**Configuration:**
- Auto-detection (Binary to Text)

**Output:**
```
Error: Invalid binary sequence.
```

**Explanation**: Binary codes must be 8-bit (8 digits each).

#### Common Use Cases

##### Morse Code Translator Use Cases
1. **Learning Morse Code**: Practice with audio playback feature
2. **Ham Radio**: Prepare messages for radio transmission
3. **Emergency Signals**: Create SOS and other emergency codes
4. **Encoding Messages**: Simple text encoding for fun or privacy
5. **Historical Communication**: Understand historical telegraph messages
6. **Educational**: Teaching Morse code in classrooms
7. **Accessibility**: Alternative communication method

##### Binary Code Translator Use Cases
1. **Computer Science Education**: Teaching binary representation
2. **Data Encoding**: Understanding how text is stored in computers
3. **Debugging**: Analyzing binary data representations
4. **Encoding Messages**: Simple binary encoding
5. **ASCII Learning**: Understanding character encoding
6. **Programming**: Binary data manipulation and analysis
7. **Cryptography**: Basic encoding for educational purposes

#### Technical Implementation

##### Class Structure
```python
class TranslatorToolsProcessor:
    """Translator tools processor with binary and Morse code translation capabilities."""
    
    # Morse code dictionary
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        # ... (40+ characters)
    }
    
    REVERSED_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
    
    @staticmethod
    def morse_translator(text, mode):
        """Translates text to or from Morse code."""
        if mode == "morse":
            return ' '.join(TranslatorToolsProcessor.MORSE_CODE_DICT.get(char.upper(), '') 
                          for char in text)
        else:  # mode == "text"
            return ''.join(TranslatorToolsProcessor.REVERSED_MORSE_DICT.get(code, '') 
                         for code in text.split(' '))
    
    @staticmethod
    def binary_translator(text):
        """Translates text to or from binary."""
        if all(c in ' 01' for c in text):  # Binary to Text
            try:
                return ''.join(chr(int(b, 2)) for b in text.split())
            except (ValueError, TypeError):
                return "Error: Invalid binary sequence."
        else:  # Text to Binary
            return ' '.join(format(ord(char), '08b') for char in text)
```

##### Widget Implementation
```python
class TranslatorToolsWidget(ttk.Frame):
    """Tabbed interface widget for translator tools."""
    
    def __init__(self, parent, app, dialog_manager=None):
        super().__init__(parent)
        self.app = app
        self.dialog_manager = dialog_manager
        self.processor = TranslatorToolsProcessor()
        
        # Audio setup (if PyAudio available)
        if PYAUDIO_AVAILABLE:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True
            )
```

##### Audio Generation (Morse Code)
```python
def _generate_morse_tone(self, duration):
    """Generate a sine wave for a given duration for Morse code."""
    tone_freq = 700  # Hz
    t = np.linspace(0, duration, int(44100 * duration), False)
    tone = np.sin(tone_freq * t * 2 * np.pi)
    return (0.5 * tone).astype(np.float32)

def _play_morse_thread(self, morse_code):
    """The actual playback logic that runs in a thread."""
    for char in morse_code:
        if char == '.':
            tone = self._generate_morse_tone(0.080)
            self.audio_stream.write(tone.tobytes())
        elif char == '-':
            tone = self._generate_morse_tone(0.240)
            self.audio_stream.write(tone.tobytes())
        elif char == ' ':
            time.sleep(0.240)  # Letter spacing
        elif char == '/':
            time.sleep(0.560)  # Word spacing
```

##### Dependencies
- **Required**: Python standard library (tkinter, threading, time modules)
- **Optional**: 
  - `pyaudio` for Morse code audio playback
  - `numpy` for audio tone generation

##### Performance Considerations
- **Morse Translation**: O(n) complexity, instant for typical text
- **Binary Translation**: O(n) complexity, efficient for all text sizes
- **Audio Playback**: Non-blocking threading, doesn't freeze UI
- **Memory Efficient**: Processes text in-place without large intermediate structures
- **Auto-Detection**: Fast pattern matching for binary detection

#### Best Practices

##### Recommended Usage
- **Morse Code**: Use uppercase for consistency (tool converts automatically)
- **Binary Code**: Ensure 8-bit codes when entering binary manually
- **Audio Playback**: Use for learning and verification, not long messages
- **Tab Selection**: Switch between tabs based on encoding type needed

##### Morse Code Tips
- Morse code output is always uppercase
- Use `/` to separate words in Morse code
- Spaces separate individual letters
- Not all special characters are supported (40+ characters available)
- Audio playback requires PyAudio installation

##### Binary Code Tips
- Auto-detection makes translation direction automatic
- Binary codes must be space-separated
- Each binary code should be 8 bits (8 digits)
- Supports full UTF-8 character set
- Invalid binary shows clear error message

##### Performance Tips
- Both translators optimized for typical text sizes
- Audio playback runs in separate thread (non-blocking)
- Memory efficient for large texts
- Auto-detection is fast and reliable

##### Common Pitfalls
- **Morse Code**: Unsupported characters are silently ignored
- **Binary Code**: Must use spaces between 8-bit codes
- **Audio**: Requires PyAudio and numpy for audio features
- **Case Sensitivity**: Morse code converts to uppercase
- **Binary Length**: Each code must be exactly 8 bits

#### Troubleshooting

##### Issue: Morse code missing characters
**Solution**: Check if the character is supported. The tool supports A-Z, 0-9, and common punctuation. Unsupported characters are silently ignored.

##### Issue: Binary translation shows error
**Solution**: Ensure binary codes are:
- Space-separated
- Exactly 8 bits each (e.g., "01001000" not "1001000")
- Only contain 0s and 1s

##### Issue: Audio playback not available
**Solution**: Install PyAudio and numpy:
```
pip install pyaudio numpy
```

##### Issue: Audio playback doesn't stop
**Solution**: Click the "Stop Playing" button or wait for playback to complete. Audio runs in a separate thread.

##### Issue: Morse to text not working
**Solution**: Ensure proper spacing:
- Spaces between letters
- `/` between words
- Example: `... --- ...` for "SOS"

##### Issue: Settings not saving
**Solution**: Ensure the application has write permissions to `settings.json`. Settings are saved separately for each translator.

#### Related Tools

- **Base64 Encoder/Decoder**: Another encoding/decoding tool
- **Find & Replace Text**: Can be used to clean input before translation
- **Case Tool**: Normalize case before Morse code translation
- **Word Frequency Counter**: Analyze translated text patterns

#### See Also
- [Encoding/Decoding Tools Overview](#encoding-decoding-tools-documentation)
- [Base64 Encoder/Decoder Documentation](#base64-encoder-decoder)
- [Text Transformation Tools](#text-transformation-tools-4-tools)

---



