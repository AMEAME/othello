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

  def initialize(board=nil)
    unless board.nil?
      @cells = board.dup
      return
    end
    @cells = Array.new(8) { [0] * 8 }
    @cells[3][4] = PLAYER
    @cells[4][3] = PLAYER
    @cells[3][3] = OPPONENT
    @cells[4][4] = OPPONENT
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
    @valid_moves.each {|e| @board[*e] = VALID }
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
    right = 1..(9 - move[0])
    bottom = 1..(9 - move[1])
    left = 1..(move[0])
    top = 1..(move[1])
    directions = {
      right: [
        right, lambda {|i| [move[0] + i, move[1]] }
      ],
      bottom: [
        bottom, lambda {|i| [move[0], move[1] + i] }
      ],
      left: [
        left, lambda {|i| [move[0] - i, move[1]] }
      ],
      top: [
        top, lambda {|i| [move[0], move[1] - i] }
      ],
      top_left: [
        [top, left].min_by {|r| r.size },
        lambda {|i| [move[0] - i, move[1] - i] }
      ],
      bottom_right: [
        [bottom, right].min_by {|r| r.size },
        lambda {|i| [move[0] + i, move[1] + i] }
      ],
      top_right: [
        [top, right].min_by {|r| r.size },
        lambda {|i| [move[0] + i, move[1] - i] }
      ],
      bottom_left: [
        [bottom, left].min_by {|r| r.size },
        lambda {|i| [move[0] - i, move[1] + i] }
      ]
    }
    directions.reduce([]) do |valid_moves, (dir, (range, calc_place))|
      valid_moves + get_flip_positions(board, range, calc_place)
    end.compact.reject(&:empty?).uniq
  end

  def get_flip_positions(board, scope, calc_place)
    scope.reduce([]) do |pos_flip, i|
      place = calc_place.call(i)
      return [] if board[*place] == EMPTY
      if board[*place] == PLAYER
        pos_flip.each do |p|
          board[*p] = PLAYER
        end
        return pos_flip
      end
      pos_flip << place
    end
  end
end


def main
  records = File.readlines('data.csv').map {|l| l.chomp.split(',') }
  othello = Othello.new
  records.each_with_index do |record, i|
    record.each do |r|
      break if r == '0'
      othello.make_move(r.split('').map(&:to_i))
    end
    puts i if i % 1000 == 0
  end
end

if __FILE__ == $0
  main
end
