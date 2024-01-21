## What about Unicode characters? Why only printable ASCII?
There are many considerations...

- For UTF-8, ASCII characters take up 1 byte each but other characters take multiple. If the other characters must take up more space, why not just stick to using multiple 1-byte ASCII characters?
- Scratch is typically not case-sensitive and there are many characters that Scratch will treat as identical. Costume names are case sensitive so the encoder/decoder uses costumes for each character which is unwieldy with the addition of more characters. 
- There is an increased risk that these other characters will not be supported, limiting the number of places this format can be used.

