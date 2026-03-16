#!/bin/bash
# Uso:
#   bash mqtt_mode.sh --secure
#   bash mqtt_mode.sh --test
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$SCRIPT_DIR/mqtt_config/mosquitto.conf"
ACL="$SCRIPT_DIR/mqtt_config/acl"
ACL_BAK="$SCRIPT_DIR/mqtt_config/acl.secure"
TEST_ACL_CONTENT=$(cat <<'EOF'
topic readwrite #

user processor
topic readwrite #

user mqtt_broker_processor
topic readwrite #
EOF
)

apply_secure() {
    if [ -f "$ACL_BAK" ]; then
        cp "$ACL_BAK" "$ACL"
    fi

    sed -i 's/^allow_anonymous true/allow_anonymous false/' "$CONF"
    grep -q '^password_file' "$CONF" || sed -i '/^acl_file/i password_file /mosquitto/config/passwd' "$CONF"

    echo "Modo seguro activado"
}

apply_test() {
    # Respaldar ACL solo si el contenido actual no es el de pruebas
    if ! diff -q <(printf '%s\n' "$TEST_ACL_CONTENT") "$ACL" >/dev/null 2>&1; then
        cp "$ACL" "$ACL_BAK"
    fi

    printf '%s\n' "$TEST_ACL_CONTENT" > "$ACL"

    sed -i 's/^allow_anonymous false/allow_anonymous true/' "$CONF"
    sed -i '/^password_file/d' "$CONF"

    echo "Modo de pruebas activado"
}

case "${1}" in
    --secure) apply_secure ;;
    --test)   apply_test ;;
    *)
        echo "Uso: bash mqtt_mode.sh --secure | --test"
        exit 1
        ;;
esac

cd "$SCRIPT_DIR"
docker compose -f docker-compose-deploy.yml restart mqtt-broker

