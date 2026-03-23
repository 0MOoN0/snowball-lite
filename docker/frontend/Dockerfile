FROM node:20-bookworm-slim AS build

ARG PNPM_VERSION=10.28.2
ARG VITE_BUILD_MODE=lite
ARG VITE_SOURCEMAP=false
ARG NODE_OPTIONS=--max-old-space-size=1536

ENV CI=true \
    PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    NODE_OPTIONS=$NODE_OPTIONS \
    VITE_SOURCEMAP=$VITE_SOURCEMAP

WORKDIR /workspace

RUN corepack enable \
    && corepack prepare pnpm@${PNPM_VERSION} --activate

COPY pnpm-workspace.yaml pnpm-lock.yaml /workspace/
RUN mkdir -p /workspace/apps/frontend
COPY apps/frontend/package.json /workspace/apps/frontend/package.json

RUN pnpm install --frozen-lockfile

COPY apps/frontend /workspace/apps/frontend

RUN pnpm --dir apps/frontend exec vite build --mode ${VITE_BUILD_MODE}

FROM nginx:1.27-alpine

COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/apps/frontend/dist-lite /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
