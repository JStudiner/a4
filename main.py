# Image compression
#
# You'll need Python 3 and must install the 'numpy' package (just for its arrays).
#
# The code also uses the 'netpbm' package, which is included in this directory.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python3 netpbm.py images/cortex.pnm
#
# NOTES:
#
#   - Use struct.pack( '>h', val ) to convert signed short int 'val' to a two-byte bytearray
#
#   - Use struct.pack( '>H', val ) to convert unsigned short int 'val' to a two-byte bytearray
#
#   - Use struct.unpack( '>H', twoBytes )[0] to convert a two-byte bytearray to an unsigned short int.  Note the [0].
#
#   - Use struct.unpack( '>' + 'H' * count, manyBytes ) to convert a bytearray of 2 * 'count' bytes to a tuple of 'count' unsigned short ints


import sys, os, math, time, struct, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify it

headerText = b'my compressed image - v1.0'



# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')

  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect whether the 'shape' has two or three components and
  # set the number of channels accordingly.  Furthermore,
  # single-channel images must be indexed as img[y,x] instead of
  # img[y,x,k].  You'll need two pieces of similar code: one piece for
  # the single-channel case and one piece for the multi-channel case.

  # Compress the image

  startTime = time.time()

  outputBytes = bytearray()

  # ---------------- [YOUR CODE HERE] ----------------
  #
  # REPLACE THE CODE BELOW WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.

  
  differences = []

  # Predictive Encoding  
  for row in range(img.shape[0]):  # Iterate through rows
    for col in range(img.shape[1]):  # Iterate through columns

      # Check if the image has one channel (ie if the image is grayscale), if so no need to loop through the channels
      if len(img.shape) ==2:

        # Check if there is a previous pixel value
        if row == 0:
          current_val = img[row, col, 0]
        else:
          current_val = int(img[row, col, 0]) - int(img[row - 1, col, 0])
        
        differences.append(str(current_val))
      
      # If the image has multiple channels, loop through each channel and calculate the difference
      else:
        for channel in range(img.shape[2]):  # Iterate through channels
          
          # Check if there is a previous pixel value
          if row == 0:
            current_val = img[row, col, channel]
          else:
            current_val = int(img[row, col, channel]) - int(img[row - 1, col, channel])
          
          differences.append(str(current_val))
  
  # Initialize LZW variables
  potential_values = map(str, range(-255, 256))
  lzw_compression_dict = {value: index for index, value in enumerate(potential_values)}
  current_str = differences[0]

  # LZW compression
  # loop through all the difference values
  for index in range(1, len(differences)):

    # check if current string + next difference is in the dictionary
    next_str = current_str + "|" + differences[index]    

    if next_str in lzw_compression_dict:
      current_str = next_str
    
    # if not output the bytes of the dictionary at the current string
    else:
      current_bytes = struct.pack(">H", lzw_compression_dict[current_str])
      outputBytes.extend(current_bytes)

      #check if the dict size is less than 65536
      if len(lzw_compression_dict) < 65536:
        lzw_compression_dict[next_str] = len(lzw_compression_dict)
      current_str = differences[index]
  
  #deal with the last value
  current_bytes = struct.pack(">H", lzw_compression_dict[current_str])
  outputBytes += current_bytes

  # ---------------- [END OF YOUR CODE] ----------------

  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( headerText + b'\n' )
  outputFile.write( bytes( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]), encoding='utf8' ) )
  outputFile.write( outputBytes )

  # Print information about the compression
  
  inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  


# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + b'\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  

  rows, columns, numChannels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  startTime = time.time()

  # ---------------- [YOUR CODE HERE] ----------------
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.
 


  # ---------------- [END OF YOUR CODE] ----------------

  endTime = time.time()
  sys.stderr.write( 'Uncompression time %.2f seconds\n' % (endTime - startTime) )

  # Output the image

  netpbm.imsave( outputFile, img )
  

  
# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)
