#!/usr/bin/env bash

LINKS=$(curl -sS https://raw.githubusercontent.com/TheOutdoorProgrammer/profile/refs/heads/main/_data/links.yml)
SOCIAL=$(curl -sS https://raw.githubusercontent.com/TheOutdoorProgrammer/profile/refs/heads/main/_data/social.yml)

shield_logo_for(){
  case "$1" in
    "YouTube")  echo "youtube"  ;;
    "BlueSky")  echo "bluesky"  ;;
    "LinkedIn") echo "linkedin" ;;
    "Email")    echo "gmail"    ;;
    *)          echo ""         ;;
  esac
}

shield_color_for(){
  case "$1" in
    "YouTube")        echo "ff5555" ;;
    "BlueSky")        echo "8be9fd" ;;
    "LinkedIn")       echo "bd93f9" ;;
    "Email")          echo "f1fa8c" ;;
    "Nerds Who Fish") echo "50fa7b" ;;
    *)                echo "6272a4" ;;
  esac
}

iconify_to_base64_logo(){
  local icon_path=$(echo "$1" | sed 's/:/\//')
  local b64=$(curl -sS "https://api.iconify.design/${icon_path}.svg" | base64 | tr -d '\n')
  echo "data:image/svg%2bxml;base64,${b64}"
}

gen_top(){
  cat <<'EOF' > README.md
![Personal Website](https://raw.githubusercontent.com/TheOutdoorProgrammer/TheOutdoorProgrammer/main/logos/theoutdoorprogrammer/the-outdoor-programmer-logo-hq.png)

<p align="center">
    <b>Hello, I'm Joey 👋</b>
</p>

EOF

  echo '<p align="center">' >> README.md

  length_of_categories=$(echo "$LINKS" | yq '.buttons | length')
  for i in $(seq 0 $((length_of_categories - 1))); do
    category=$(echo "$LINKS" | yq -r ".buttons[$i].category")
    if [ "$category" != "Where You Can Find Me" ]; then
      continue
    fi

    length_of_items=$(echo "$LINKS" | yq ".buttons[$i].items | length")
    for j in $(seq 0 $((length_of_items - 1))); do
      title=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].title")
      url=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].url")

      if [ "$title" = "GitHub" ]; then
        continue
      fi

      logo=$(shield_logo_for "$title")
      color=$(shield_color_for "$title")
      label=$(echo "$title" | sed 's/ /_/g')

      if [ -z "$logo" ]; then
        icon=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].icon")
        logo=$(iconify_to_base64_logo "$icon")
      fi

      echo "  <a href=\"${url}\"><img src=\"https://img.shields.io/badge/${label}-${color}?style=for-the-badge&logo=${logo}&logoColor=282a36\" /></a>" >> README.md
    done
    break
  done

  length_of_social=$(echo "$SOCIAL" | yq '. | length')
  for s in $(seq 0 $((length_of_social - 1))); do
    title=$(echo "$SOCIAL" | yq -r ".[$s].name")
    url=$(echo "$SOCIAL" | yq -r ".[$s].url")
    icon=$(echo "$SOCIAL" | yq -r ".[$s].icon")
    color=$(shield_color_for "$title")
    label=$(echo "$title" | sed 's/ /_/g')
    logo=$(iconify_to_base64_logo "$icon")
    echo "  <a href=\"${url}\"><img src=\"https://img.shields.io/badge/${label}-${color}?style=for-the-badge&logo=${logo}&logoColor=282a36\" /></a>" >> README.md
  done

  echo '</p>' >> README.md
  echo '' >> README.md
}

gen_hcl_intro(){
  cat <<'EOF' >> README.md
```hcl
resource "github_introduction" "joey" {
    name      = "Joey Stout"
    role      = "Solutions Architect @ Spacelift"
    interests = ["kubernetes", "opentofu", "nodejs", "python", "gitops"]
    hobbies   = ["fishing", "hunting", "outdoors"]
}
```

EOF
}

gen_tech_badges(){
  cat <<'EOF' >> README.md
<p align="center">
  <img src="https://img.shields.io/badge/Kubernetes-50fa7b?style=flat-square&logo=kubernetes&logoColor=282a36" />
  <img src="https://img.shields.io/badge/OpenTofu-bd93f9?style=flat-square&logo=opentofu&logoColor=282a36" />
  <img src="https://img.shields.io/badge/Python-f1fa8c?style=flat-square&logo=python&logoColor=282a36" />
  <img src="https://img.shields.io/badge/Node.js-50fa7b?style=flat-square&logo=nodedotjs&logoColor=282a36" />
  <img src="https://img.shields.io/badge/Go-8be9fd?style=flat-square&logo=go&logoColor=282a36" />
  <img src="https://img.shields.io/badge/GitOps-ff79c6?style=flat-square&logo=git&logoColor=282a36" />
</p>

EOF
}

gen_blusky_posts(){
  echo "### 🦋 Latest from BlueSky" >> README.md
  echo "" >> README.md

  MAX_POSTS=${MAX_POSTS:-3}
  posts=$(curl -sS -H "Accept: application/json" "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=theoutdoorprogrammer.com&limit=${MAX_POSTS}")

  length=$(echo "$posts" | jq ".feed | length")
  if [ "$length" -le 0 ] 2>/dev/null; then
    return
  fi

  col_width=$((100 / length))

  echo "<table><tr>" >> README.md

  for i in $(seq 0 $((length - 1))); do
      text=$(echo "$posts" | jq -r ".feed[$i].post.record.text" | tr '\n' ' ' | xargs)
      uri=$(echo "$posts" | jq -r ".feed[$i].post.uri" | awk -F'/' '{print $NF}')
      date=$(echo "$posts" | jq -r ".feed[$i].post.record.createdAt")
      date=${date%%T*}
      handle=$(echo "$posts" | jq -r ".feed[$i].post.author.handle")
      post_url="https://bsky.app/profile/${handle}/post/${uri}"

      thumb=$(echo "$posts" | jq -r ".feed[$i].post.embed.images[0].thumb // empty" 2>/dev/null)
      alt=$(echo "$posts" | jq -r ".feed[$i].post.embed.images[0].alt // empty" 2>/dev/null)

      # Use alt text as fallback when post has no body text
      if [ -z "$text" ] && [ -n "$alt" ]; then
        text="$alt"
      fi

      if [ "$handle" != "theoutdoorprogrammer.com" ]; then
        text="🔄 @$handle: $text"
      fi

      # HTML-escape user content
      text=$(echo "$text" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
      alt=$(echo "$alt" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')

      echo "<td width=\"${col_width}%\" valign=\"top\" align=\"center\">" >> README.md

      if [ -n "$thumb" ]; then
        echo "<a href=\"${post_url}\"><img src=\"${thumb}\" width=\"150\" alt=\"${alt}\" /></a><br/>" >> README.md
      fi

      if [ -n "$text" ]; then
        echo "${text}<br/><br/>" >> README.md
      fi

      echo "<sub><a href=\"${post_url}\">${date}</a></sub>" >> README.md
      echo "</td>" >> README.md
  done

  echo "</tr></table>" >> README.md
  echo "" >> README.md
}

iconify_img(){
  local icon="$1"
  if [ -n "$icon" ] && [ "$icon" != "null" ]; then
    local icon_path=$(echo "$icon" | sed 's/:/\//')
    echo "<img src=\"https://api.iconify.design/${icon_path}.svg?color=%23f8f8f2\" width=\"20\" height=\"20\" /> "
  fi
}

gen_collapsible_sections(){
  length_of_categories=$(echo "$LINKS" | yq '.buttons | length')

  for i in $(seq 0 $((length_of_categories - 1))); do
    category=$(echo "$LINKS" | yq -r ".buttons[$i].category")

    # Skip social links — handled by badges
    if [ "$category" = "Where You Can Find Me" ] || [ "$category" = "Spacelift" ]; then
      continue
    fi

    # Emoji per category
    case "$category" in
      "Projects") emoji="🔧" ;;
      "Spacelift") emoji="🚀" ;;
      "Blog Posts") emoji="📝" ;;
      *) emoji="📌" ;;
    esac

    echo "### ${emoji} ${category}" >> README.md
    echo "" >> README.md


    first_desc=$(echo "$LINKS" | yq -r ".buttons[$i].items[0].description" 2>/dev/null)
    use_table=false
    if [ -n "$first_desc" ] && [ "$first_desc" != "null" ]; then
      use_table=true
      echo "| | Name | Description |" >> README.md
      echo "|:-:|------|-------------|" >> README.md
    fi

    length_of_items=$(echo "$LINKS" | yq ".buttons[$i].items | length")

    for j in $(seq 0 $((length_of_items - 1))); do
      title=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].title")
      url=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].url")
      icon=$(iconify_img "$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].icon")")

      if [ "$use_table" = true ]; then
        desc=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].description" 2>/dev/null)
        if [ "$desc" = "null" ] || [ -z "$desc" ]; then
          desc=""
        fi
        desc=$(echo "$desc" | sed 's/|/\\|/g')
        echo "| ${icon}| [${title}](${url}) | ${desc} |" >> README.md
      else
        echo "- ${icon}[${title}](${url})" >> README.md
      fi
    done

    echo "" >> README.md
  done

  for i in $(seq 0 $((length_of_categories - 1))); do
    category=$(echo "$LINKS" | yq -r ".buttons[$i].category")
    if [ "$category" != "Spacelift" ]; then
      continue
    fi

    echo "### 🚀 ${category}" >> README.md
    echo "" >> README.md

    length_of_items=$(echo "$LINKS" | yq ".buttons[$i].items | length")
    for j in $(seq 0 $((length_of_items - 1))); do
      title=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].title")
      url=$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].url")
      icon=$(iconify_img "$(echo "$LINKS" | yq -r ".buttons[$i].items[$j].icon")")
      echo "- ${icon}[${title}](${url})" >> README.md
    done

    echo "" >> README.md
    break
  done
}

# Generate the README
gen_top
gen_tech_badges
gen_hcl_intro
gen_blusky_posts
gen_collapsible_sections
