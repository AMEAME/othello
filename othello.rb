require 'forwardable'

EMPTY = 0
PLAYER = 1
OPPONENT = 2
VALID = 3

DISK_MARK = {
  EMPTY => '-',
  PLAYER => 'o',
  OPPONENT => 'x',
  VALID => '.',
}

class Board
  extend Forwardable
  def_delegators :@cells, :each, :map, :map!
  attr_reader :cells

  def initialize(board=nil)
    if board.nil?
      @cells = Array.new(8) {[0] * 8 }
      @cells[3][4] = PLAYER
      @cells[4][3] = PLAYER
      @cells[3][3] = OPPONENT
      @cells[4][4] = OPPONENT
    else
      @cells = board.dup
    end
  end

  def []=(disc_row, disc_col, value)
    @cells[disc_col - 1][disc_row - 1] = value
  end

  def [](disc_row, disc_col)
    return EMPTY unless (1..8).to_a.include?(disc_row) &&
                        (1..8).to_a.include?(disc_col)
    @cells[disc_col - 1][disc_row - 1]
  end

  def dup
    @cells.map(&:dup).dup
  end

  def to_s
    '  ' + (1..8).map {|i| "#{i} " }.join + "\n" +
      @cells.each_with_index.reduce('') do |str, (row, i)|
        "#{str}#{i + 1} #{row.reduce('') {|a, e| a + "#{DISK_MARK[e]} " }}\n"
      end + "\n"
  end
end


class Othello
  attr_reader :board

  def initialize
    @board = Board.new
    @valid_moves = []
    update_valid_moves
  end

  def make_move(move)
    @valid_moves.each {|e| @board[*e] = EMPTY }
    flip_disks(@board, move)
    switch_turn
    update_valid_moves
    switch_turn if @valid_moves.empty?
  end

  def update_valid_moves
    @valid_moves.clear
    (1..8).each do |row|
      (1..8).each do |col|
        if @board[row, col] == EMPTY
          board = Board.new(@board)
          @valid_moves << [row, col] unless flip_disks(board, [row, col]).empty?
        end
      end
    end
    @valid_moves.uniq!
    @valid_moves.each {|e| @board[*e] = VALID }
  end

  def switch_turn
    @board.map! do |row|
      row.map do |cell|
        cell = cell == PLAYER ? OPPONENT : PLAYER if cell != EMPTY
        cell
      end
    end
  end

  def to_s
    @board.to_s
  end

  private
  def flip_disks(board, move)
    board[*move] = PLAYER
    right  = 1..(8 - move[0])
    bottom = 1..(8 - move[1])
    left   = 1..(move[0] - 1)
    top    = 1..(move[1] - 1)
    directions = {
      right:  [right,  [ 1,  0]],
      bottom: [bottom, [ 0,  1]],
      left:   [left,   [-1,  0]],
      top:    [top,    [ 0, -1]],
      top_left:     [[top, left].min_by {|r| r.size },     [-1, -1]],
      bottom_right: [[bottom, right].min_by {|r| r.size }, [ 1,  1]],
      top_right:    [[top, right].min_by {|r| r.size },    [ 1, -1]],
      bottom_left:  [[bottom, left].min_by {|r| r.size },  [-1,  1]]
    }
    directions.reduce([]) do |valid_moves, (dir, (range, pos))|
      valid_moves + get_flip_positions(board, range, move, *pos)
    end.reject(&:empty?).uniq
  end

  def get_flip_positions(board, range, move, x, y)
    range.reduce([]) do |pos_flip, i|
      pos = [move[0] + x * i, move[1] + y * i]
      break if board[*pos] == EMPTY
      if board[*pos] == PLAYER
        pos_flip.each {|p| board[*p] = PLAYER }
        return pos_flip
      end
      pos_flip << pos
    end
    []
  end
end


def serialize_board_str(board)
  board.cells.reduce('') do |str, row|
    str + row.reduce('') {|a, e| a + e.to_s }
  end
end

def main
  files = Dir.glob('WTH/*')
  records = []
  files.each do |f|
    data = File.open(f, 'rb').each_byte.map {|e| e }
    data[16..data.size - 1].each_slice(68).map {|e| e[8..67] }.each {|g| records << g }
  end
  encoding = lambda {|s| (s / 10 - 1) * 8 + s % 10 - 1 }
  output_data = []
  [records[0]].each_with_index do |record, i|
    othello = Othello.new
    record.each do |r|
      break if r == 0
      puts r
      output_data << serialize_board_str(othello.board) + " #{encoding.call(r)}"
      othello.make_move([r / 10, r % 10])
      puts othello
    end
    puts "#{i}: \n#{othello}" if i % 100 == 0
  end
  File.open('othello.data', 'w') {|f| output_data.each {|d| f.puts d } }
end

if __FILE__ == $0
  s = Time.now
  main
  puts "#{Time.now - s}s"
end
