library(tidyverse)

setwd("home/ubuntu/da_design_server20181480/data")

# Netflix Korea 랭킹 산출
youtube_nf_kr <- read.csv("netflix_korea.csv")

youtube_nf_kr$view <- as.numeric(gsub('\\D','', youtube_nf_kr$view))

kr_title_str <- youtube_nf_kr$title
kr_content_name <- c("익스트랙션", "보건교사 안은영", "스위트홈", "빈센조",
                     "페르소나", "슬기로운 의사생활", "옥자", "승리호", 
                     "경이로운 소문", "킹덤", "낙원의 밤", "비밀의 숲", 
                     "라바 아일랜드", "기묘한 이야기", "인간수업",
                     "내가 사랑했던 모든 남자들에게", "악마는 사라지지 않는다",
                     "설국열차", "좋아하면 울리는", "위쳐", "키싱 부스",
                     "차인표", "도도솔솔라라솔", "블랙핑크", "범인은 바로",
                     "콜", "에놀라 홈즈", "아미 오브 더 데드", "YG전자",
                     "시카고7", "스타트업", "퍼펙트 데이트", "아케인",
                     "첫사랑은 처음이라서", "유성화원", "라바 아일랜드",
                     "러브, 데스", "올드 가드", "6 언더그라운드", "폴라")

for(str in kr_content_name){
  
  num <- grep(str, kr_title_str)
  
  kr_title_str[num] <- str
}

youtube_nf_kr$title <- kr_title_str

kr_nf_rank <- youtube_nf_kr %>%
  group_by(title) %>%
  summarise(sum = sum(view)) %>%
  arrange(desc(sum))


# ------------------------------------------------------------------------------
# Netflix UK 랭킹 산출
youtube_nf_uk <- read.csv("netflix_uk.csv")

youtube_nf_uk$view <- as.numeric(gsub('\\D','', youtube_nf_uk$view))

uk_title_str <- tolower(youtube_nf_uk$title)
uk_content_name <- c("stranger things", "big mouth", "we can be heroes",
                     "riverdale", "eurovision", "sex education",
                     "over the moon", "addams", "formula 1",
                     "brooklyn nine-nine", "elf", "friends", "the queen's gambit",
                     "pose", "top boy", "stand-up", "bridgerton", "the crown",
                     "the king", "cobra kai", "drag race", "umbrella academy")

for(str in uk_content_name){
  
  num <- grep(str, uk_title_str)
  
  uk_title_str[num] <- str
}

youtube_nf_uk$title <- uk_title_str

uk_nf_rank <- youtube_nf_uk %>%
  group_by(title) %>%
  summarise(sum = sum(view)) %>%
  arrange(desc(sum))

uk_nf_rank[1:15,1] <- c("기묘한 이야기", "오티스의 비밀 상담소", "빅 마우스",
                        "리버데일", "유로비전 송 콘테스트", "더 크라운",
                        "오늘부터 히어로", "프렌즈", "브룩클린 나인-나인",
                        "스탠드업", "오버 더 문", "퀸스갬빗", "아담스 패밀리",
                        "탑 보이", "브리저튼")

# ------------------------------------------------------------------------------
# Netflix USA 랭킹 산출
youtube_nf_usa <- read.csv("netflix_usa.csv")

youtube_nf_usa$view <- as.numeric(gsub('\\D','', youtube_nf_usa$view))

usa_title_str <- tolower(youtube_nf_usa$title)
usa_content_name <- c("sacred games", "mitchells", "bird box", "witcher",
                      "stranger things", "our planet", "breaking bad",
                      "#realityhigh", "cuites", "kissing booth",
                      "devil all the time", "lust stories", "extraction",
                      "perfect date", "lucifer", "beasts of no nation",
                      "marvel's", "13 reasons why", "gerald's game",
                      "army of the dead", "narcos", "bright", "money heist",
                      "enola holmes", "brain on fire", "6 underground")

for(str in usa_content_name){
  
  num <- grep(str, usa_title_str)
  
  usa_title_str[num] <- str
}

youtube_nf_usa$title <- usa_title_str

usa_nf_rank <- youtube_nf_usa %>%
  group_by(title) %>%
  summarise(sum = sum(view)) %>%
  arrange(desc(sum))

usa_nf_rank[1:15,1] <- c("우리의 지구", "기묘한 이야기", "키씽 부스", "신성한 게임",
                         "위쳐", "브레이킹 배드", "마블 시리즈 드라마", "미첼 가족과 기계 전쟁",
                         "버드박스", "러스트 스토리", "루시퍼", "종이의 집", 
                         "#리얼리티 하이", "큐티스", "악마는 사라지지 않는다")
write.csv(usa_nf_rank, "USA_netflix_ranking.csv")

# ------------------------------------------------------------------------------
# 디시인사이드 5월 작성글 저장
gall_netflix <- read.csv("netflix_gall.csv")
gall_netflix <- subset(gall_netflix, str_sub(gall_netflix$date, 6, 7) == "05")
write.csv(gall_netflix, "netflix_gall_may.csv")
