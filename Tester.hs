
module Tester where
import System.Directory
import Data.List (sort, sortBy)
import Data.List.Split (splitOn)
import Lexer (runLexer)

-- Auxilliaries

readInt = read :: String -> Int

boolToInt :: Bool -> Int
boolToInt True  = 1
boolToInt False = 0

cmpSetDirs :: String -> String -> Ordering
cmpSetDirs dir1 dir2 = compare idx1 idx2
    where idx1 = Tester.readInt $ last $ splitOn "." dir1
          idx2 = Tester.readInt $ last $ splitOn "." dir2

-- Testing functions

testerDir = "tests/"

runTest :: Int -> String -> Int -> IO Float
runTest stage setName testNo =
    do stageDir <- return $ ("T" ++ (show stage) ++ "/")
       lexerSpec <- readFile (testerDir ++ stageDir
                                        ++ setName ++ "/"
                                        ++ setName ++ ".lex")
       input <- readFile (testerDir ++ stageDir
                                    ++ setName ++ "/input/"
                                    ++ setName ++ "."
                                    ++ show testNo ++ ".in")
       ref <- readFile (testerDir ++ stageDir
                                  ++ setName ++ "/ref/"
                                  ++ setName ++ "."
                                  ++ show testNo ++ ".ref")

       output <- return $ runLexer lexerSpec input

       formatRes <- return $ (filter (/="") . lines)
       cmp <- return $ (formatRes output) == (formatRes ref)

       no_dots <- return 20
       setNo <- return $ Tester.readInt $ last $ splitOn "." setName
       setNoPara  <- return $ boolToInt (setNo > 9)
       testNoPara <- return $ boolToInt (testNo > 9)
       dots <- return $ replicate (20 - setNoPara - testNoPara) '.'

       score <- return $ case cmp of
                            True  -> case setNo of
                                        1 -> 2.5
                                        _ -> 1
                            False -> 0
       case score of
            0 -> putStrLn (setName ++ "." ++ show testNo ++ dots ++ "failed [0p]")
            _ -> putStrLn (setName ++ "." ++ show testNo ++ dots ++ "passed [" ++ show score ++ "p]")

       return score

runSet :: Int -> String -> IO Float
runSet stage setName =
    do setDir <- return $ (testerDir ++ "T" ++ (show stage) ++ "/" ++ setName ++ "/input")
       testNos <- do inputFiles <- listDirectory setDir
                     return $ sort $
                              map Tester.readInt $
                              map (last . init . splitOn ".") inputFiles
       testScores <- mapM (runTest stage setName) testNos
       setTotal <- return $ foldl (+) 0 testScores

       putStrLn ("Set total" ++ replicate 17 '.' ++ "[" ++ show setTotal ++ "p]\n")
       return setTotal

runAll :: Int -> IO ()
runAll 3 = putStrLn "Stage 3 checker coming soon"
runAll 2 = putStrLn "Stage 2 checker coming soon"
runAll stage =
    do stageDir <- return $ (testerDir ++ "T" ++ (show stage) ++ "/")
       setNames <- listDirectory stageDir >>= (return . sortBy cmpSetDirs)
       setTotals <- mapM (runSet stage) setNames
       total <- return $ foldl (+) 0 setTotals

       putStrLn ("Total" ++ replicate 21 '.' ++ "[" ++ show total ++ "p]")

