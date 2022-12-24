#include <stdlib.h>             /* malloc */
#include <stdio.h>              /* printf */
#include <string.h>             /* memset */
#include <time.h>               /* time, clock, clock_t */
#include <inttypes.h>           /* uint64_t */

#define HT_BUCKETS 1000

struct ht {
        struct bucket {
                void *value;
                char *key;
                struct bucket *next;
        } **bucket;

        unsigned num_keys;
};

void ht_init(struct ht *h)
{
        memset(h, 0, sizeof *h);
        h->bucket = malloc(HT_BUCKETS * sizeof *h->bucket);
        memset(h->bucket, 0, HT_BUCKETS * sizeof *h->bucket);
}

uint64_t hash(char *d)
{
	uint64_t hash = 5381;
        size_t len = strlen(d);

	for (size_t i = 0; i < len; i++)
		hash = ((hash << 5) + hash) + d[i];

	return hash % HT_BUCKETS;
}
void ht_add(struct ht *h, char *key, void *value)
{
        unsigned bucket_index = hash(key);
        struct bucket **b = &h->bucket[bucket_index];
        while (*b && strcmp((*b)->key, key)) b = &(*b)->next;
        if (!*b) {
                *b = malloc(sizeof *b);
                **b = (struct bucket) {
                        .key = key,
                        .value = value,
                        .next = 0,
                };
        } else {
                (*b)->value = value;
        }
}

void *ht_get(struct ht *h, char *key)
{
        unsigned bucket_index = hash(key);
        struct bucket *b = h->bucket[bucket_index];
        while (b && strcmp(b->key, key)) b = b->next;
        return b ? b->value : 0;
}

void random_string(char **string)
{
        unsigned len = 1 + rand() % 10;
        *string = malloc(len + 1);
        for (unsigned i = 0; i < len; i++)
                (*string)[i] = 'a' + (rand() % 26);
        (*string)[len] = 0;
}

struct value {
        enum {
                VALUE_INT,
                VALUE_STRING,
        } type;

        union {
                int integer;
                char *string;
        };

        char *key;
} vals[10000];

unsigned nvals;

void value_show(struct value *v)
{
        switch (v->type) {
        case VALUE_INT:
                printf("%d\n", v->integer);
                break;
        case VALUE_STRING:
                printf("%s\n", v->string);
                break;
        }
}

struct value *value_get(char *key)
{
        for (unsigned i = 0; i < nvals; i++)
                if (!strcmp(vals[i].key, key))
                        return vals + i;
        return NULL;
}

int main(void)
{
        srand(time(0));

        struct ht *h = malloc(sizeof *h);
        ht_init(h);

        for (unsigned i = 0; i < sizeof vals / sizeof *vals; i++) {
                char *key;
                random_string(&key);

                if (value_get(key)) {
                        i--;
                        free(key);
                        continue;
                }

                vals[i].key = key;

                switch ((vals[i].type = rand() % 2)) {
                case VALUE_INT:
                        vals[i].integer = rand() % 1000;
                        break;
                case VALUE_STRING:
                        random_string(&vals[i].string);
                        break;
                }

                ht_add(h, vals[i].key, vals + i);
                nvals++;
        }

        static char *lookups[sizeof vals / sizeof *vals];

        for (unsigned i = 0; i < nvals; i++)
                lookups[i] = vals[rand() % nvals].key;

        clock_t begin = clock();
        for (unsigned i = 0; i < nvals; i++) ht_get(h, lookups[i]);
        clock_t ht_time = clock() - begin;

        begin = clock();
        for (unsigned i = 0; i < nvals; i++) value_get(lookups[i]);
        clock_t linear_time = clock() - begin;

        printf("hash table is %.0lf times faster (%ld vs. %ld)\n",
               (double)linear_time / (double)ht_time,
               ht_time, linear_time);
}
